from click.testing import CliRunner

from ggrep.cli import cli


class TestCli:
    def test_no_pattern(self):
        """
        A regex pattern must be given on the command line.
        """
        runner = CliRunner()
        result = runner.invoke(cli, [])
        assert result.exit_code == 2
        assert "Missing argument 'PATTERN'" in result.output

    def test_no_files(self):
        """
        At least one filename must be given on the command line.
        """
        runner = CliRunner()
        result = runner.invoke(cli, ["pattern"])
        assert result.exit_code == 2
        assert "Missing argument 'FILENAMES...'" in result.output
