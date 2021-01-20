import click

from pypi_stats_utils.data_fetcher import PyPiDataFetcher

CONTEXT_SETTINGS = {'max_content_width': 300}


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('package', required=True)
@click.option('-fields', '-f', multiple=True, required=False, help='Filed names')
@click.option('--csv', '-c', is_flag=True, default=True, help='Print data in CSV format')
@click.option('--print_header', '-p', is_flag=True, default=False, help='Print header in case of CSV format')
@click.option('--timeout', '-t', type=int, default=120000, help='Milliseconds. Default: 120000 (2 minutes)')
@click.option('--days', '-d', default=0, help='Number of days in the past to include. Default: 0')
@click.option('--all', 'all_installers', is_flag=True, default=True,
              help='Show downloads by all installers, not only pip.')
@click.version_option()
@click.pass_context
def cli(
    ctx,
    package,
    fields,
    csv,
    print_header,
    timeout,
    days,
    all_installers,
):
    if package is None and not fields:
        click.echo(ctx.get_help())
        return

    data_fetcher = PyPiDataFetcher(
        package=package,
        header_fields=fields,
        timeout=timeout,
        days=days,
        all_installers=all_installers
    )

    download_data = data_fetcher.get_stats()
    if download_data:
        headers, *data = download_data
        if csv:
            if print_header:
                click.echo('{}'.format(",".join(headers)))
            for entry in data:
                click.echo('{}'.format(",".join(entry)))
