#!/usr/bin/env python
import click, os, subprocess

@click.group()
def cli():
    pass

@cli.command()
def list():
    chains = ['INPUT', 'OUTPUT', 'TRAFFIC_QUOTA']

    while True:
        if click.confirm('开始查看链上的记录？'):
            for n, c in enumerate(chains):
                entry = str(n) + ' - ' + c
                click.echo(entry)
            select_chain = click.prompt('请选择要查看的链编号', default=1, type=int)
            cmd = ['sudo', 'iptables', '-L', chains[select_chain], '-nv', '--line-number']
            subprocess.run(cmd)
        else:
            break


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

@cli.command()
def add():
    click.echo('功能初始化...')
    cmd_traffic_chain = 'sudo iptables -N TRAFFIC_QUOTA'
    add_traffic_chain = subprocess.run(cmd_traffic_chain.split(), capture_output=True)
    if add_traffic_chain.returncode:
        click.echo('已存在 TRAFFIC_QUOTA 链 [跳过]')
    else:
        click.echo('创建 TRAFFIC_QUOTA 链 [完成]')
        # 添加流量限额规则, 50GB
        cmd_quota_1 = 'sudo iptables -A TRAFFIC_QUOTA -m quota --quota 50000000000 -j ACCEPT'
        cmd_quota_2 = 'sudo iptables -A TRAFFIC_QUOTA -j DROP'
        add_quota_accept = subprocess.run(cmd_quota_1.split(), capture_output=True)
        if add_quota_accept.returncode:
            click.echo(add_quota_accept.stderr)
        else:
            click.echo('创建 流量限额接受规则 [完成]')
        add_auota_drop = subprocess.run(cmd_quota_2.split(), capture_output=True)
        if add_auota_drop.returncode:
            click.echo(add_auota_drop.stderr)
        else:
            click.echo('创建 流量限额拒绝规则 [完成]')
        click.echo('初始化完成！')

    while True:
        if click.confirm('是否创新的新的防火墙规则？'):
            # TODO 输入端口规则验证
            ports = click.prompt('请输入要开放的端口号，用逗号分隔多个端口，用冒号设置端口段')
            cmd_1 = 'sudo iptables -I INPUT -p tcp -m multiport --sports %s -g TRAFFIC_QUOTA' % ports
            cmd_2 = 'sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -g TRAFFIC_QUOTA' % ports
            add_ports_input = subprocess.run(cmd_1.split(), capture_output=True)
            if add_ports_input.returncode:
                click.echo('创建指定端口的入站规则 [失败]')
                click.echo(add_ports_input.stderr)
                break
            else:
                click.echo('创建指定端口的入站规则 [完成]')

            add_ports_output = subprocess.run(cmd_2.split(), capture_output=True)
            if add_ports_output.returncode:
                click.echo('创建指定端口的出站规则 [失败]')
                click.echo(add_ports_output.stderr)
                break
            else:
                click.echo('创建指定端口的出站规则 [完成]')

            # 打印规则列表
            chains = ['INPUT', 'OUTPUT', 'TRAFFIC_QUOTA']

            for c in chains:
                rules = 'sudo iptables -L %s -nv' % c
                subprocess.run(rules.split())
                
        else:
            break

if __name__ == '__main__':
    cli()