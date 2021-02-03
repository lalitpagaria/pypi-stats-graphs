import collections
import csv
from datetime import datetime

import click
import matplotlib.pyplot as plt

from pypi_stats_utils.data_fetcher import PyPiDataFetcher

CONTEXT_SETTINGS = {'max_content_width': 300}

DEFAULT_FIELDS_CSV = [
    "date",
    "country",
    "version",
    "installer",
    "system",
    "distro",
    "cpu",
    "system-release",
    "pyversion"
]

DOWNLOAD_COUNT_FIELD = "download_count"
DATE_FIELD = "date"


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.argument('package', required=True)
@click.option('-fields', '-f', multiple=True, required=False, help='Filed names')
@click.option('--print_csv', '-c', is_flag=True, help='Print data in CSV format')
@click.option('--generate_graph', '-g', is_flag=True, help='Print graph')
@click.option('--y_field', '-x', help='Y axis field')
@click.option('--use_csv', help='Use provided CSV file to generated graph')
@click.option('--print_header', '-p', is_flag=True, help='Print header in case of CSV format')
@click.option('--timeout', '-t', type=int, default=120000, help='Milliseconds. Default: 120000 (2 minutes)')
@click.option('--days', '-d', default=0, help='Number of days in the past to include. Default: 0')
@click.option('--all', '-a', 'all_installers', is_flag=True, help='Show downloads by all installers, not only pip.')
@click.version_option()
@click.pass_context
def cli(
        ctx,
        package,
        fields,
        print_csv,
        generate_graph,
        y_field,
        use_csv,
        print_header,
        timeout,
        days,
        all_installers,
):
    if package is None and not fields:
        click.echo(ctx.get_help())
        return

    fields = fields or DEFAULT_FIELDS_CSV
    y_field = y_field or "country"

    if use_csv is None:
        data_fetcher = PyPiDataFetcher(
            package=package,
            header_fields=fields,
            timeout=timeout,
            days=days,
            all_installers=all_installers
        )

        download_data = data_fetcher.get_stats()
    else:
        download_data = []
        with open(use_csv, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                download_data.append(row)

    if download_data:
        headers, *data = download_data
        headers = list(headers)
        data = list(data)
        if print_csv:
            if print_header:
                click.echo('{}'.format(",".join(headers)))
            for entry in data:
                click.echo('{}'.format(",".join(entry)))
        elif generate_graph:
            y_field_name = PyPiDataFetcher.get_parsed_fields([y_field])[0][0]
            y_field_index = headers.index(y_field_name)
            x_field_name = PyPiDataFetcher.get_parsed_fields([DATE_FIELD])[0][0]
            x_field_index = headers.index(x_field_name)
            download_count_index = headers.index(DOWNLOAD_COUNT_FIELD)

            x_field_set = set([row[x_field_index] for row in data])
            y_map = dict()
            for row in data:
                if row[y_field_index] not in y_map:
                    y_map[row[y_field_index]] = {x_field: 0 for x_field in x_field_set}
                data_map = y_map[row[y_field_index]]
                data_map[row[x_field_index]] = data_map[row[x_field_index]] + int(row[download_count_index])


            plt.xlabel(x_field_name)
            plt.ylabel(DOWNLOAD_COUNT_FIELD)
            plt.xticks(rotation='vertical', fontsize=8)
            plt.yticks(fontsize=8)
            for key, value in y_map.items():
                x_list = []
                y_list = []
                ord_dict = collections.OrderedDict(
                    sorted(value.items(), key=lambda item: datetime.strptime(item[0], '%Y-%m-%d')))
                for k, v in ord_dict.items():
                    x_list.append(k)
                    y_list.append(v)

                plt.plot(x_list, y_list, label=key, markersize=6, marker='o')

            plt.margins(0.2)
            # Tweak spacing to prevent clipping of tick-labels
            plt.subplots_adjust(bottom=0.25)
            plt.ylim(bottom=0)
            plt.legend()
            plt.show()
