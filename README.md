
# imageset

## Overview

![](https://img.shields.io/badge/Python-3.12-blue)
![](https://img.shields.io/badge/License-AGPLv3-blue)

`Pillow` による画像読み込み・書き込み機能を代行します。

画像の書き込み・読み込み機能を代行し、実際の保存を遅延することにより、非可逆圧縮形式の多重保存による劣化を防止することができます。

## Usage

同一画像に対する操作を繰り返した場合の実行例

```py
from imageset import ImageSet

with ImageSet() as image_set:
  
  image = image_set.open("sample.jpg")
  image.thumbnail((100, 100))
  image_set.save("sample.jpg", image) #実際に保存せず保存の指示だけを行う
  
  image2 = image_set.open("sample.jpg")
  image2.thumbnail((50, 50))
  image_set.save("sample .jpg", image2) #実際に保存せず保存の指示だけを行う

#... with コンテキスト後に変更された画像だけが保存されます
```

変更されていない画像を保存した場合の実行例

```py
from imageset import ImageSet

with ImageSet() as image_set:
  image = image_set.open("sample.jpg")
  image_set.save("sample.jpg", image) #変更されていない画像を保存する

#... 画像は変更されていないので保存されない
```

## Install

```shell
pip install .
```

### Test

```shell
pip install .[test]
pytest .
```

### Document

```py
import imageset

help(imageset)
```

## Donation

<a href="https://buymeacoffee.com/tikubonn" target="_blank"><img src="doc/img/qr-code.png" width="3000px" height="3000px" style="width:150px;height:auto;"></a>

もし本パッケージがお役立ちになりましたら、少額の寄付で支援することができます。<br>
寄付していただいたお金は書籍の購入費用や日々の支払いに使わせていただきます。
ただし、これは寄付の多寡によって継続的な開発やサポートを保証するものではありません。ご留意ください。

If you found this package useful, you can support it with a small donation.
Donations will be used to cover book purchases and daily expenses.
However, please note that this does not guarantee ongoing development or support based on the amount donated.

## License

© 2025 tikubonn

imageset licensed under the [AGPLv3](./LICENSE).
