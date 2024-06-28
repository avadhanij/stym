dist:
    python3 -m build --wheel

develop:
    uv pip install -e .

clean:
    rm -rf build
    rm -rf dist
    rm -rf spotoytm.egg-info