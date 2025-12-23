
import pytest
import hashlib
from imageset import _HashDigest

def test_hash_digest ():

  #基本機能の動作確認です

  hash_digest = _HashDigest.from_data("md5", b"abc")
  assert hash_digest.algorithm == "md5"
  hs = hashlib.new("md5")
  hs.update(b"abc")
  assert hash_digest.digest == hs.digest()
  assert hash_digest.is_modified(b"abc") == False
  assert hash_digest.is_modified(b"def") == True
