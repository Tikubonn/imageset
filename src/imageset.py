
import hashlib
from abc import ABC, abstractmethod
from PIL import Image
from PIL.ImageFile import ImageFile
from typing import NamedTuple, Self, Any
from pathlib import Path
from closeable import ICloseable, Closeable

class _HashDigest (NamedTuple):

  algorithm:str
  digest:bytes

  @classmethod
  def _calc_digest (cls, algorithm:str, data:bytes) -> bytes:
    hs = hashlib.new(algorithm)
    hs.update(data)
    return hs.digest()

  def is_modified (self, data:bytes) -> bool:
    digest = self._calc_digest(self.algorithm, data)
    return digest != self.digest

  @classmethod
  def from_data (cls, algorithm:str, data:bytes) -> Self:
    digest = cls._calc_digest(algorithm, data)
    return cls(algorithm, digest)

class ImageSet (ICloseable):

  """画像の読み込み・保存処理をシミュレートします。

  画像の保存処理をシミュレートすることにより、非可逆圧縮で多重保存する行為を回避します。
  また、変更された画像だけを保存する機能により、画像の劣化を防止します。

  読み込まれた画像は `PIL.ImageFile.ImageFile` インスタンスとして返されます。

  Examples
  --------
  >>> with ImageSet() as image_set:
  >>>   image = image_set.open("sample.jpg")
  >>>   image_min = image.thumbnail((320, 240))
  >>>   image_set.save(image_min, "sample.min.jpg")
  """

  def __init__ (self, hash_algorithm:str="md5", *, make_dir:bool=False):

    """インスタンスの初期化を行います。

    Parameters
    ----------
    hash_algorithm : str
      画像が変更されたか否かを判定するために用いられるハッシュアルゴリズム名です。
      未指定ならば `md5` が設定されます。
    make_dir : bool
      画像保存時に親ディレクトリの作成を行うかを設定します。
      未指定ならば `False` が設定されます。
    """

    self.hash_algorithm = hash_algorithm
    self._make_dir = make_dir
    self._closeable = Closeable(self._on_close)
    self._images = {}

  @property
  def closed (self) -> bool:
    return self._closeable.closed

  def _on_close (self, succeeded:bool):
    for path, (image, digest, save_params) in self._images.items():
      if succeeded and digest.is_modified(image.tobytes()) or save_params:
        if self._make_dir:
          path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, **save_params)
      image.close()

  def close (self, _succeeded:bool=True):
    self._closeable.close(_succeeded)

  def __enter__ (self):
    return self

  def __exit__ (self, exc_type, exc_value, traceback):
    self.close((
      exc_type is None and 
      exc_value is None and 
      traceback is None
    ))

  def open (self, path:Path|str) -> ImageFile:

    """指定された画像を読み込みます。

    Warnings
    --------
    本メソッドにより作成されたインスタンスは `ImageSet.close` が実行されるまでキャッシュされ続けるため、
    `ImageFile.close` メソッドによる手動での開放は行ってはなりません。

    Parameters
    ----------
    Path : Path|str
      読み込む画像ファイルのパスです。

    Returns
    -------
    ImageFile
      指定されたパスの画像を読み込んだインスタンスを返します。
      既に読み込まれた・保存された画像が指定されていた場合、このメソッドはキャッシュされた画像インスタンスを返します。

    Raises
    ------
    imageset.CloseableStateError
      本オブジェクトが既に閉じられていた時に送出される例外です。
    """

    self._closeable.must_be_open()
    if path not in self._images:
      image = Image.open(path)
      digest = _HashDigest.from_data(self.hash_algorithm, image.tobytes())
      self._images[path] = (image, digest, {})
    image, _, _ = self._images[path]
    return image

  def save (self, path:Path|str, image:ImageFile, *, save_params:dict[str, Any]={}):

    """画像を指定されたファイルに保存します。

    Parameters
    ----------
    path : Path|str
      保存先の画像ファイルのパスです。
    image : ImageFile
      保存する画像のインスタンスです。
    save_params : dict[str, Any]
      保存する際に指定するオプショナル引数です。
      未指定ならば空の辞書が設定されます。

    Raises
    ------
    imageset.CloseableStateError
      本オブジェクトが既に閉じられていた時に送出される例外です。
    """

    self._closeable.must_be_open()
    if path in self._images:
      _, digest, _ = self._images[path]
      self._images[path] = (image.copy(), digest, save_params)
    else:
      digest = _HashDigest.from_data(self.hash_algorithm, b"")
      self._images[path] = (image.copy(), digest, save_params)
