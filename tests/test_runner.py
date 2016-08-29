import mock
import os
import subprocess
import unittest
from skipper import runner


USER_ID = 1000
GROUP_ID = 2000

REGISTRY = 'registry.io:5000'
IMAGE = 'image'
TAG = '1234567'
FQDN_IMAGE = REGISTRY + '/' + IMAGE + ':' + TAG

WORKDIR = '/home/adir/work'
PROJECT = 'proj'
PROJECT_DIR = os.path.join(WORKDIR, PROJECT)

ENV = ["KEY1=VAL1", "KEY2=VAL2"]


class TestRunner(unittest.TestCase):
    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_simple_command_not_nested(self, popen_mock):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['pwd']
        runner.run(command)
        popen_mock.assert_called_once_with(
            command,
            stdout=subprocess.PIPE
        )

    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_complex_command_not_nested(self, popen_mock):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['ls -l']
        runner.run(command)
        popen_mock.assert_called_once_with(
            command,
            stdout=subprocess.PIPE
        )

    @mock.patch('os.getuid', autospec=True, return_value=USER_ID)
    @mock.patch('os.getcwd', autospec=True, return_value=PROJECT_DIR)
    @mock.patch('grp.getgrnam', autospec=True,)
    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_simple_command_nested(self, popen_mock, getgrnam_mock, *args):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['pwd']
        getgrnam_mock.return_value.gr_gid = GROUP_ID
        runner.run(command, FQDN_IMAGE)
        expected_nested_command = [
            'docker', 'run',
            '--rm',
            '--net', 'host',
            '-v', '%(workdir)s:/workspace:rw,Z' % dict(workdir=WORKDIR),
            '-v', '/var/lib/osmosis:/var/lib/osmosis:rw,Z',
            '-v', '/var/run/docker.sock:/var/run/docker.sock:Z',
            '-u', '%(uid)s:%(gid)s' % dict(uid=USER_ID, gid=GROUP_ID),
            '-w', '/workspace/proj',
            '--entrypoint', command[0],
            FQDN_IMAGE
        ]
        popen_mock.assert_called_once_with(
            expected_nested_command,
            stdout=subprocess.PIPE
        )

    @mock.patch('os.getuid', autospec=True, return_value=USER_ID)
    @mock.patch('os.getcwd', autospec=True, return_value=PROJECT_DIR)
    @mock.patch('grp.getgrnam', autospec=True,)
    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_simple_command_nested_with_env(self, popen_mock, getgrnam_mock, *args):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['pwd']
        getgrnam_mock.return_value.gr_gid = GROUP_ID
        runner.run(command, FQDN_IMAGE, ENV)
        expected_docker_command = [
            'docker', 'run',
            '--rm',
            '--net', 'host',
            '-e', 'KEY1=VAL1',
            '-e', 'KEY2=VAL2',
            '-v', '%(workdir)s:/workspace:rw,Z' % dict(workdir=WORKDIR),
            '-v', '/var/lib/osmosis:/var/lib/osmosis:rw,Z',
            '-v', '/var/run/docker.sock:/var/run/docker.sock:Z',
            '-u', '%(uid)s:%(gid)s' % dict(uid=USER_ID, gid=GROUP_ID),
            '-w', '/workspace/proj',
            '--entrypoint', command[0],
            FQDN_IMAGE
        ]
        popen_mock.assert_called_once_with(
            expected_docker_command,
            stdout=subprocess.PIPE
        )

    @mock.patch('os.getuid', autospec=True, return_value=USER_ID)
    @mock.patch('os.getcwd', autospec=True, return_value=PROJECT_DIR)
    @mock.patch('grp.getgrnam', autospec=True,)
    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_complex_command_nested(self, popen_mock, getgrnam_mock, *args):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['ls', '-l']
        getgrnam_mock.return_value.gr_gid = GROUP_ID
        runner.run(command, FQDN_IMAGE)
        expected_nested_command = [
            'docker', 'run',
            '--rm',
            '--net', 'host',
            '-v', '%(workdir)s:/workspace:rw,Z' % dict(workdir=WORKDIR),
            '-v', '/var/lib/osmosis:/var/lib/osmosis:rw,Z',
            '-v', '/var/run/docker.sock:/var/run/docker.sock:Z',
            '-u', '%(uid)s:%(gid)s' % dict(uid=USER_ID, gid=GROUP_ID),
            '-w', '/workspace/proj',
            '--entrypoint', command[0],
            FQDN_IMAGE,
            command[1]
        ]
        popen_mock.assert_called_once_with(
            expected_nested_command,
            stdout=subprocess.PIPE
        )

    @mock.patch('os.getuid', autospec=True, return_value=USER_ID)
    @mock.patch('os.getcwd', autospec=True, return_value=PROJECT_DIR)
    @mock.patch('grp.getgrnam', autospec=True,)
    @mock.patch('subprocess.Popen', autospec=False)
    def test_run_complex_command_nested_with_env(self, popen_mock, getgrnam_mock, *args):
        popen_mock.return_value.stdout.readline.side_effect = ['aaa', 'bbb', 'ccc', '']
        popen_mock.return_value.poll.return_value = -1
        command = ['ls', '-l']
        getgrnam_mock.return_value.gr_gid = GROUP_ID
        runner.run(command, FQDN_IMAGE, ENV)
        expected_nested_command = [
            'docker', 'run',
            '--rm',
            '--net', 'host',
            '-e', 'KEY1=VAL1',
            '-e', 'KEY2=VAL2',
            '-v', '%(workdir)s:/workspace:rw,Z' % dict(workdir=WORKDIR),
            '-v', '/var/lib/osmosis:/var/lib/osmosis:rw,Z',
            '-v', '/var/run/docker.sock:/var/run/docker.sock:Z',
            '-u', '%(uid)s:%(gid)s' % dict(uid=USER_ID, gid=GROUP_ID),
            '-w', '/workspace/proj',
            '--entrypoint', command[0],
            FQDN_IMAGE,
            command[1]
        ]
        popen_mock.assert_called_once_with(
            expected_nested_command,
            stdout=subprocess.PIPE
        )