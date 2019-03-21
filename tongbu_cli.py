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
@click.option('-q', '--quota', 'quota', required=True ,help='下行流量限额')
def addport(port, quota):
    try:
        os.system('sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -j DROP' % port)
        os.system('sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -m quota --quota %s -j ACCEPT' % (port, quota))
        os.system('sudo iptables -L OUTPUT -nv --line-number')
    except Exception as e:
        click.echo(e)


@cli.command()
@click.option('-n', '--line-number', required=True, help='行编号')
def delport(line_number):
    os.system('sudo iptables -D OUTPUT %i' % int(line_number))
    os.system('sudo iptables -L OUTPUT -nv --line-number')
if __name__ == '__main__':
    cli()