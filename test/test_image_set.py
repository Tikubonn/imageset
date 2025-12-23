
import time
import pytest
import shutil
from PIL import Image
from PIL.ImageFile import ImageFile
from pathlib import Path
from imageset import ImageSet
from closeable import CloseableStateError

TEST_DIR = Path("./.test")
TEST_FILE = TEST_DIR.joinpath("sample.png")

def setup_function (func):
  TEST_DIR.mkdir(parents=True, exist_ok=True)
  image = Image.new("RGB", (100, 100), (255, 255, 255))
  image.save(TEST_FILE)

def teardown_function (func):
  shutil.rmtree(TEST_DIR)

SLEEP_AMOUNT:int = 2

def test_image_set ():

  #画像を変更しなかった場合の動作確認です
  
  time.sleep(SLEEP_AMOUNT)
  last_file_stat = TEST_FILE.stat()

  with ImageSet() as image_set:
    image = image_set.open(TEST_FILE)
    assert isinstance(image, ImageFile)
    image_set.save(TEST_FILE, image)

  time.sleep(SLEEP_AMOUNT)
  assert last_file_stat.st_mtime == TEST_FILE.stat().st_mtime

def test_image_set2 ():

  #画像を変更せず、保存パラメータのみを指定した場合の動作確認です
  
  time.sleep(SLEEP_AMOUNT)
  last_file_stat = TEST_FILE.stat()

  with ImageSet() as image_set:
    image = image_set.open(TEST_FILE)
    assert isinstance(image, ImageFile)
    image_set.save(TEST_FILE, image, save_params={"compress_level": 0})

  time.sleep(SLEEP_AMOUNT)
  assert last_file_stat.st_mtime != TEST_FILE.stat().st_mtime
  assert last_file_stat.st_size < TEST_FILE.stat().st_size

def test_image_set3 ():

  #画像を変更した場合の動作確認です
  
  time.sleep(SLEEP_AMOUNT)
  last_file_stat = TEST_FILE.stat()

  with ImageSet() as image_set:
    image = image_set.open(TEST_FILE)
    assert isinstance(image, ImageFile)
    image.thumbnail((image.width // 2, image.height // 2))
    image_set.save(TEST_FILE, image)

  time.sleep(SLEEP_AMOUNT)
  assert last_file_stat.st_mtime != TEST_FILE.stat().st_mtime
  assert last_file_stat.st_size > TEST_FILE.stat().st_size

def test_image_save ():

  #保存される画像が本体ではなく複製であることを検証します(本体がそのまま保存されていると、副作用のある操作を行ったときに、保存された画像にも影響がでてしまう)

  with ImageSet() as image_set:
    image = image_set.open(TEST_FILE)
    image.thumbnail((image.width // 2, image.height // 2))
    image_set.save(TEST_FILE, image)
    saved_size = image.size
    image.thumbnail((image.width // 2, image.height // 2)) #保存後に画像を 1/4 の幅に変更します
    saved_image = image_set.open(TEST_FILE)
    assert saved_image.size == saved_size

def test_image_set_close ():

  #閉じられた状態で操作を行ったときの動作確認です

  image_set = ImageSet()
  image_set.close()

  #閉じられた状態で ImageSet.open が実行されると例外が送出されます

  with pytest.raises(CloseableStateError):
    image_set.open(TEST_FILE)

  #閉じられた状態で ImageSet.open が実行されると例外が送出されます

  with pytest.raises(CloseableStateError):
    with Image.new("RGB", (100, 100), (255, 255, 255)) as image:
      image_set.save(TEST_FILE, image)
