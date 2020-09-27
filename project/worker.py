import subprocess

command = ['D:',
           'cd nip_project\nip',
           '..\venv\Scripts\activate',
           'python -m celery -A project worker -l info -P solo']

# subprocess.run(comm, shell=True)

cmd_line = "echo Hello!"
p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
(output, err) = p.communicate()
p_status = p.wait()
print("Command output: " + str(output))
