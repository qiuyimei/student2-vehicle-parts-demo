import hashlib
import zipfile
from pathlib import Path
import pytest
from scripts import download_dataset as module


def make_archive(path):
    with zipfile.ZipFile(path, 'w') as archive:
        for split in ['train', 'test']:
            archive.writestr(f'images/{split}/car.jpg', b'example-image')
            archive.writestr(f'labels/{split}/car.txt', '0 0 0 1 0 1 1\n')


def test_archive_cannot_escape_destination(tmp_path):
    path = tmp_path / 'unsafe.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('../outside.txt', 'must not escape')
    with zipfile.ZipFile(path) as archive, pytest.raises(ValueError):
        module.validate_archive(archive, tmp_path / 'output')
    assert not (tmp_path / 'outside.txt').exists()


def test_wrong_checksum_does_not_extract_files(tmp_path):
    path = tmp_path / 'wrong.zip'
    make_archive(path)
    with pytest.raises(ValueError, match='SHA256'):
        module.extract_dataset(path, tmp_path / 'output')
    assert not (tmp_path / 'output').exists()


def test_test_subset_excludes_training_files(tmp_path, monkeypatch):
    path = tmp_path / 'dataset.zip'
    make_archive(path)
    monkeypatch.setattr(module, 'SHA256', hashlib.sha256(path.read_bytes()).hexdigest())
    monkeypatch.setattr(module, 'EXPECTED', {'test': 1, 'train': 1, 'val': 0})
    output = tmp_path / 'output'
    summary = module.extract_dataset(path, output, 'test')
    assert (output / 'images/test/car.jpg').exists()
    assert (output / 'labels/test/car.txt').exists()
    assert not (output / 'images/train').exists()
    assert summary['splits'] == {'test': 1}


def test_unexpected_image_count_fails_before_extraction(tmp_path, monkeypatch):
    path = tmp_path / 'dataset.zip'
    make_archive(path)
    monkeypatch.setattr(module, 'SHA256', hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError, match='图片数异常'):
        module.extract_dataset(path, tmp_path / 'output', 'test')


def test_unknown_subset_is_rejected(tmp_path):
    with pytest.raises(ValueError, match='subset'):
        module.extract_dataset(tmp_path / 'not-needed.zip', tmp_path / 'output', 'invalid')
