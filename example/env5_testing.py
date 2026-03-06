import elasticai.experiment_framework.remote_control as rc
import click
from time import sleep

@rc.main.command
@click.pass_obj
@click.argument("data", type=str)
def my_custom_command(obj, data):
  rc_handle = rc.RemoteControl(obj)
  my_cmd_id = 250
  result = rc_handle.send_command(my_cmd_id, data, len(data))
  print(result)


@rc.main.command
@click.pass_obj
def enable_reset(obj):
  rc_handle = rc.RemoteControl(obj)
  rc_handle.send_command(251, "",0)


@rc.main.command
@click.pass_obj
def disable_reset(obj):
  rc_handle = rc.RemoteControl(obj)
  rc_handle.send_command(252, "", 0)


@rc.main.command
@click.pass_obj
def do_reset(obj):
  rc_handle = rc.RemoteControl(obj)
  for _ in range(10):
      rc_handle.send_command(251, "", 0)
      sleep(0.01)
      rc_handle.send_command(252, "", 0)
      sleep(0.01)


if __name__ == '__main__':
    rc.main()
