import os
import subprocess
import pytest

class Bash:
    def __init__(self, envvars=None):
        self.env = os.environ.copy()
        if envvars:
            self.env.update(envvars)
        self.auto_return_code_error = True
        self.process = subprocess.Popen(
            ['bash'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            env=self.env,
            bufsize=0
        )

    def __call__(self, *, envvars=None):
        envvars = envvars or {}
        bash = self

        class _Context:
            def __enter__(self_inner):
                for k, v in envvars.items():
                    bash.send(f'export {k}="{v}"')
                return bash

            def __exit__(self_inner, exc_type, exc, tb):
                for k in envvars.keys():
                    bash.send(f'unset {k}')
                return False

        return _Context()

    def send(self, command):
        if self.process.poll() is not None:
            raise RuntimeError('Bash process is not running')
        sentinel = '__RET_END__'
        self.process.stdin.write(command + "\n")
        self.process.stdin.write(f"echo $?{sentinel}\n")
        self.process.stdin.flush()
        output_lines = []
        ret_code = 0
        while True:
            line = self.process.stdout.readline()
            if line == '':
                # process exited
                break
            if line.rstrip().endswith(sentinel):
                ret_code = int(line.rstrip().replace(sentinel, ''))
                break
            output_lines.append(line.rstrip())
        output = "\n".join(output_lines)
        if self.auto_return_code_error and ret_code != 0:
            raise RuntimeError(output)
        return output

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.write('exit\n')
            self.process.stdin.flush()
            self.process.wait()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

@pytest.fixture
def bash(request):
    envvars = getattr(request, 'param', None)
    bash_obj = Bash(envvars=envvars)
    try:
        yield bash_obj
    finally:
        bash_obj.close()
