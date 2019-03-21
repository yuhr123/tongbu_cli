#!/usr/bin/env python
import click, os

@click.group()
def cli():
    pass

@cli.command()
def list():
    os.system('sudo iptables -L OUTPUT -nv --line-number')

@cli.command()
@click.option('-p', '--port', 'port', required=True ,help='监控的端口号')
@click.option('-q', '--quota', 'quota', required=True, default=10000000000,help='下行流量限额，默认：10GB')
def addport(port, quota):
    if click.confirm('是否配置流量限额？'):
        quota = click.prompt('请输入流量限额(单位 Byte)', default=quota, type=int)
        try:
            os.system('sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -j DROP' % port)
            os.system('sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -m quota --quota %s -j ACCEPT' % (port, str(quota)))
            os.system('sudo iptables -L OUTPUT -nv --line-number')
        except Exception as e:
            click.echo(e)
    else:
        try:
            os.system('sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -j ACCEPT' % port)
            os.system('sudo iptables -L OUTPUT -nv --line-number')
        except Exception as e:
            click.echo(e)


@cli.command()
def delport():
    os.system('sudo iptables -L OUTPUT -nv --line-number')
    line_number = click.prompt('请输入要删除的规则编号', type=int)
    os.system('sudo iptables -D OUTPUT %i' % int(line_number))
    os.system('sudo iptables -L OUTPUT -nv --line-number')
    while True:
        if click.confirm('是否继续删除规则？'):
            os.system('sudo iptables -L OUTPUT -nv --line-number')
            line_number = click.prompt('请输入要删除的规则编号', type=int)
            os.system('sudo iptables -D OUTPUT %i' % int(line_number))
            os.system('sudo iptables -L OUTPUT -nv --line-number')
        else:
            click.echo('Bye!')
            break
if __name__ == '__main__':
    cli()