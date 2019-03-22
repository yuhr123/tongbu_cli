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
    quota_chains = {
        'TRAFFIC_QUOTA_10GB': 10000000000,
        'TRAFFIC_QUOTA_30GB': 30000000000,
        'TRAFFIC_QUOTA_60GB': 60000000000,
        'TRAFFIC_QUOTA_100GB': 100000000000,
    }
    for k, v in quota_chains.items():
        cmd = 'sudo iptables -N %s' % k
        add_traffic_chain = subprocess.run(cmd.split(), capture_output=True)

        if add_traffic_chain.returncode:
            click.echo('已存在 %s 链 [跳过]' % k)
        else:
            click.echo('创建 %s 链 [完成]' % k)
            cmd_quota_1 = 'sudo iptables -A %s -m quota --quota %s -j ACCEPT' % (k, str(v))
            cmd_quota_2 = 'sudo iptables -A %s -j DROP' % k
            add_quota_accept = subprocess.run(cmd_quota_1.split(), capture_output=True)
            if add_quota_accept.returncode:
                click.echo(add_quota_accept.stderr)
            else:
                click.echo('创建 %s 流量限额接受规则 [完成]' % k)
            add_auota_drop = subprocess.run(cmd_quota_2.split(), capture_output=True)
            if add_auota_drop.returncode:
                click.echo(add_auota_drop.stderr)
            else:
                click.echo('创建 %s 流量限额拒绝规则 [完成]' % k)
            click.echo('初始化完成！')

    while True:
        if click.confirm('是否创新的新的防火墙规则？'):
            # TODO 输入端口规则验证
            ports = click.prompt('请输入要开放的端口号，用逗号分隔多个端口，用冒号设置端口段')
            click.echo('要配置的端口：%s' % ports)
            for k in quota_chains:
                click.echo(k)
            select_chain = click.prompt('请选择流量限额配置')

            cmd_1 = 'sudo iptables -I INPUT -p tcp -m multiport --sports %s -g %s' % (ports, select_chain)
            cmd_2 = 'sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -g %s' % (ports, select_chain)

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
            chains = ['INPUT', 'OUTPUT']

            for c in chains:
                rules = 'sudo iptables -L %s -nv' % c
                subprocess.run(rules.split())

        else:
            break

if __name__ == '__main__':
    cli()
