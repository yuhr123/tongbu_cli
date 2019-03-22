#!/usr/bin/env python
import click
import os
import subprocess


@click.group()
def cli():
    """本工具用于 iptables 的端口流量监控规则管理"""
    pass


@cli.command()
def list():
    """查看指定链上的规则"""
    chains = [
        'INPUT',
        'OUTPUT',
        'TRAFFIC_QUOTA_10GB',
        'TRAFFIC_QUOTA_30GB',
        'TRAFFIC_QUOTA_60GB',
        'TRAFFIC_QUOTA_100GB',
    ]

    while True:
        if click.confirm('开始查看链上的记录？'):
            for n, c in enumerate(chains):
                entry = str(n) + ' - ' + c
                click.echo(entry)
            select_chain = click.prompt('请选择要查看的链编号', default=1, type=int)
            cmd = ['sudo', 'iptables', '-L',
                   chains[select_chain], '-nv', '--line-number']
            subprocess.run(cmd)
        else:
            break


@cli.command()
def addrule():
    """添加开放端口规则"""
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
            cmd_quota_1 = 'sudo iptables -A %s -m quota --quota %s -j ACCEPT' % (
                k, str(v))
            cmd_quota_2 = 'sudo iptables -A %s -j DROP' % k
            add_quota_accept = subprocess.run(
                cmd_quota_1.split(), capture_output=True)
            if add_quota_accept.returncode:
                click.echo(add_quota_accept.stderr)
            else:
                click.echo('创建 %s 流量限额接受规则 [完成]' % k)
            add_auota_drop = subprocess.run(
                cmd_quota_2.split(), capture_output=True)
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

            cmd_1 = 'sudo iptables -I INPUT -p tcp -m multiport --sports %s -g %s' % (
                ports, select_chain)
            cmd_2 = 'sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -g %s' % (
                ports, select_chain)

            add_ports_input = subprocess.run(
                cmd_1.split(), capture_output=True)
            if add_ports_input.returncode:
                click.echo('创建指定端口的入站规则 [失败]')
                click.echo(add_ports_input.stderr)
                break
            else:
                click.echo('创建指定端口的入站规则 [完成]')

            add_ports_output = subprocess.run(
                cmd_2.split(), capture_output=True)
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


@cli.command()
def delrule():
    """删除指定链上的规则"""
    chains = ['INPUT', 'OUTPUT']
    while True:
        for n, c in enumerate(chains):
            click.echo(str(n) + ' - ' + c)
        select_chain = click.prompt('请选择要操作的链编号', default=1, type=int)

        while True:
            list_cmd = 'sudo iptables -L %s -nv --line-number' % chains[select_chain]
            subprocess.run(list_cmd.split())
            if click.confirm('是否要删除规则？'):
                select_rule = click.prompt('请输入规则编号', type=int)
                del_cmd = 'sudo iptables -D %s %i' % (
                    chains[select_chain], select_rule)
                del_rule = subprocess.run(del_cmd.split(), capture_output=True)
                if del_rule.returncode:
                    click.echo(del_rule.stderr)
                    break
                else:
                    click.echo('删除编号为 %i 的规则 [成功]' % select_rule)
            else:
                break


if __name__ == '__main__':
    cli()
