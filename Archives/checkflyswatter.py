# Sending Button Signal from Engagement Station to Activate flyswatter.py at Home Station
import pexpect

# Function to execute remote script
def execute_remote_script():
    host = 'ipaddy'  # replace with your remote host
    username = 'chief'  # replace with your username
    password = '1qaz2wsx#EDC$RFV'  # replace with your password

    # Command to execute the remote script with the result and tail number
    command = f'echo {password} | sudo -S python3 ~/Desktop/lights.py'  # replace with the correct path to lights.py on the remote host
    ssh_command = f'ssh {username}@{host} "{command}"'
    
    try:
        child = pexpect.spawn(ssh_command)
        child.expect('password:')
        child.sendline(password)
        child.interact()
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"SSH connection error: {e}")

# Call Function
execute_remote_script()