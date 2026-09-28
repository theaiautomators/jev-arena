"""Compatibility entry point for the curated Full v2 public report."""
import runpy


if __name__ == '__main__':
    runpy.run_module('scripts.export_builder_report', run_name='__main__')
