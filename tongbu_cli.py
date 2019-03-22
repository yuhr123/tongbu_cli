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
    chains = ['ALL', 'INPUT', 'OUTPUT', '自定义']

    while True:
        if click.confirm('开始查看链上的记录？'):
            for n, c in enumerate(chains):
                entry = str(n) + ' - ' + c
                click.echo(entry)
            select_chain = click.prompt('请选择要查看的链编号', default=0, type=int)
            if select_chain == 0:
                cmd = 'sudo iptables -L -nv --line-number'
            elif select_chain == 3:
                list_cmd = 'sudo iptables -nv -L | grep \'Chain TQ\''
                os.system(list_cmd)
                # list_cmd = ['sudo', 'iptables', '-nv', '-L', '| grep "Chain TQ"']
                # list_chain = subprocess.run(list_cmd, capture_output=True)
                # if list_chain.returncode:
                #     click.echo(list_chain.stderr)
                #     click.echo('未找到流量限额相关的链！')
                # else:
                #     click.echo(list_chain.stdout)
                the_chain = click.prompt('请输入要查看的链名')
                cmd = 'sudo iptables -L %s -nv --line-number' % the_chain
            else:
                cmd = 'sudo iptables -L %s -nv --line-number' % chains[select_chain]
            subprocess.run(cmd.split())
        else:
            break


@cli.command()
def addrule():
    """添加开放端口规则"""
    while True:
        if click.confirm('是否创新的新的防火墙规则？'):
            # TODO 输入端口规则验证
            ports = click.prompt('请输入要开放的端口号，用逗号分隔多个端口，用冒号设置端口段')
            if click.confirm('是否要为端口 %s 设置流量配额？' % ports):
                input_name = click.prompt('请输入配额链的名字，例如：18000-100G', type=str)
                chain_name = 'TQ-' + input_name
                click.echo('将使用 %s 作为限额链的名称' % chain_name)
                quota = click.prompt('请输入配额总量 Byte', type=int)
                chain_cmd = 'sudo iptables -N %s' % chain_name
                add_chain = subprocess.run(chain_cmd.split(), capture_output=True)
                if add_chain.returncode:
                    click.echo(add_chain.stderr)
                    break
                else:
                    click.echo('创建 %s 链 [完成]' % chain_name)
                    cmd_quota_1 = 'sudo iptables -A %s -m quota --quota %s -j ACCEPT' % (chain_name, quota)
                    cmd_quota_2 = 'sudo iptables -A %s -j DROP' % chain_name
                    add_quota_accept = subprocess.run(
                        cmd_quota_1.split(), capture_output=True)
                    if add_quota_accept.returncode:
                        click.echo(add_quota_accept.stderr)
                    else:
                        click.echo('创建 %s 流量限额接受规则 [完成]' % chain_name)
                    add_auota_drop = subprocess.run(
                        cmd_quota_2.split(), capture_output=True)
                    if add_auota_drop.returncode:
                        click.echo(add_auota_drop.stderr)
                    else:
                        click.echo('创建 %s 流量限额拒绝规则 [完成]' % chain_name)

                    cmd_1 = 'sudo iptables -I INPUT -p tcp -m multiport --sports %s -g %s' % (ports, chain_name)
                    cmd_2 = 'sudo iptables -I OUTPUT -p tcp -m multiport --sports %s -g %s' % (ports, chain_name)
            
            else:
                cmd_1 = 'sudo iptables -I INPUT -p tcp -m multiport --sports %s' % ports
                cmd_2 = 'sudo iptables -I OUTPUT -p tcp -m multiport --sports %s' % ports

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


@cli.command()
def delchain():
    """删除给定的链"""
    while True:
        if click.confirm('是否要删除防火墙的链？'):
            list_chain = 'sudo iptables -L'
            subprocess.run(list_chain.split())
            chain = click.prompt('请输入要删除的链名称')
            while True:
                del_rule_cmd = 'sudo iptables -D %s 1' % chain
                del_rule = subprocess.run(del_rule_cmd.split(), capture_output=True)
                if del_rule.returncode:
                    del_chain_cmd = 'sudo iptables -X %s' % chain
                    subprocess.run(del_chain_cmd.split())
                    click.echo('删除 %s [成功]' % chain)
                    break
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
