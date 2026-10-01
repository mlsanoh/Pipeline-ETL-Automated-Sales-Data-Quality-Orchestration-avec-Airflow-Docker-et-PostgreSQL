import pandas as pd
from include import artifacts


def test_artifacts_preserve_types_and_isolate_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(artifacts, 'ARTIFACT_DIR', tmp_path)
    frame = pd.DataFrame({'id': pd.Series([1, None], dtype='Int64'),
                          'date': pd.to_datetime(['2026-01-01', None])})
    first = artifacts.write_artifact(frame, 'manual/run-one', 'raw')
    second = artifacts.write_artifact(frame, 'manual/run-two', 'raw')
    assert isinstance(first, str)
    assert first != second
    pd.testing.assert_frame_equal(artifacts.read_artifact(first), frame)
    replacement = frame.iloc[:1]
    assert artifacts.write_artifact(replacement, 'manual/run-one', 'raw') == first
    pd.testing.assert_frame_equal(artifacts.read_artifact(first), replacement)
