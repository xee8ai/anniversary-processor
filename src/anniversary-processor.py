#!/usr/bin/env python3

import calendar
import configparser
import datetime
import os.path
import re
import subprocess
import sys
from xeeTools import dd, ex_to_str

try:
    import pdfkit
    PDFKIT_IMPORTED = True
except ImportError as ex:
    PDFKIT_IMPORTED = False

################################################################################
################################################################################
class BaseProcessor():
    '''This is the base class holding all methods re-used by derived classes.'''

    data = dict()

    month_names = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
        }


################################################################################
    def __init__(self):
        self._set_env()
        self._readConfig()
        self._prepare_data()


################################################################################
    def _set_env(self):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.config_dir = os.path.join(script_dir[:-3], 'etc')
        self.template_dir = os.path.join(script_dir[:-3], 'templates')
        self.output_dir = os.path.join(script_dir[:-3], 'output')


################################################################################
    def run(self):

        print('No output from BaseProcessor')


################################################################################
    def _readConfig(self):
        self.config = dict()
        # using RawConfigParser with optionxform preserves the case
        self.config['monthly'] = configparser.RawConfigParser()
        self.config['monthly'].read(os.path.join(self.config_dir, 'monthly.cfg'))
        self.config['monthly'].optionxform = str
        self.config['yearly'] = configparser.RawConfigParser()
        self.config['yearly'].optionxform = str
        self.config['yearly'].read(os.path.join(self.config_dir, 'yearly.cfg'))


################################################################################
    def _prepare_data(self):

        this_year = datetime.datetime.now().year
        next_year = this_year + 1

        year_regex = re.compile('[12][0-9]{3}')

        for interval in self.config.keys():

            for section in self.config[interval].sections():

                if self.config[interval].has_option(section, 'symbol'):
                    symbol = self.config[interval].get(section, 'symbol')
                else:
                    symbol = '?'

                for option in self.config[interval].options(section):
                    if option ==  'symbol':
                        continue

                    tmp = self.config[interval].get(section, option)
                    cur_key = '{}'.format(this_year) + '-' + tmp[-5:]
                    next_key = '{}'.format(next_year) + '-' + tmp[-5:]

                    if cur_key not in self.data.keys():
                        self.data[cur_key] = []
                    if next_key not in self.data.keys():
                        self.data[next_key] = []

                    cur_data = symbol + '  {}'.format(option)
                    next_data = symbol + '  {}'.format(option)

                    if year_regex.match(tmp[:4]):
                        age = this_year - int(tmp[:4])
                        cur_data += ' ({})'.format(age)
                        next_data += ' ({})'.format(age + 1)

                    self.data[cur_key].append(cur_data)
                    self.data[next_key].append(next_data)



################################################################################
################################################################################
class ShellProcessor(BaseProcessor):
    '''This holds the functionality to get anniversaries to your shell.'''

    lines = []

################################################################################
    def run(self):
        self._build_lines()
        self._print()


################################################################################
    def _build_lines(self):

        last_week = (datetime.datetime.today() - datetime.timedelta(7)).strftime('%Y-%m-%d')
        today = (datetime.datetime.today()).strftime('%Y-%m-%d')
        next_week = (datetime.datetime.today() + datetime.timedelta(7)).strftime('%Y-%m-%d')
        next_month = (datetime.datetime.today() + datetime.timedelta(30)).strftime('%Y-%m-%d')

        self.lines.append('')

        last_time = ''

        for date, entries in sorted(self.data.items()):

            if date < last_week:
                continue

            if date > next_month:
                continue

            for entry in entries:

                if date < today:
                    cur_time = 'last_week'
                elif date == today:
                    cur_time = 'today'
                elif date <= next_week:
                    cur_time = 'next_week'
                else:
                    cur_time = 'next_month'

                if last_time and last_time != cur_time:
                    self.lines.append('')

                line = '{}:    {}'.format(date, entry)
                line = self._prepare_line(line, cur_time)

                self.lines.append(line)

                last_time = cur_time

        self.lines.append('')


################################################################################
    def _prepare_line(self, line, line_time):
        '''Use this method in your derived classes to e.g. colorize the lines.'''

        return line


################################################################################
    def _print(self):
        for line in self.lines:
            print(line)


################################################################################
    def test_output(self):

        testlines = []
        print(self._prepare_line('last_week', 'last_week'))
        print(self._prepare_line('today', 'today'))
        print(self._prepare_line('next_week', 'next_week'))
        print(self._prepare_line('next_month', 'next_month'))



################################################################################
################################################################################
class BashProcessor(ShellProcessor):
    '''This holds the functionality to get anniversaries to your bash.'''


################################################################################
    def _prepare_line(self, line, line_time):
        '''Use this method in your derived classes to e.g. colorize the lines.'''

        colors = {
                'last_week': '\033[0;31m',
                'today': '\033[1;31m',
                'next_week': '\033[0;32m',
                'next_month': '\033[0;36m',
                'clear': '\033[0m',
                }

        line = colors[line_time] + line + colors['clear']

        return line



################################################################################
################################################################################
class PowershellProcessor(ShellProcessor):
    '''This holds the functionality to get anniversaries to your powershell.'''


################################################################################
    def _prepare_line(self, line, line_time):
        '''Use this method in your derived classes to e.g. colorize the lines.'''

        colors = {
                'last_week':    'last week    ',
                'today':        'TODAY!!      ',
                'next_week':    'next week    ',
                'next_month':   'next month   ',
                'clear': '',
                }

        line = colors[line_time] + line + colors['clear']

        return line



################################################################################
################################################################################
class HtmlProcessor(BaseProcessor):


################################################################################
    def run(self):
        self._read_template()

        for self.year in (datetime.datetime.now().year, datetime.datetime.now().year + 1):
            for self.month in range(1, 13):
                self._create_html()
                self._write_html('{}-{:02d}'.format(self.year, self.month))


################################################################################
    def _read_template(self):
        tpl_file = os.path.join(self.template_dir, 'html', 'month.tpl.htm')
        with open(tpl_file, 'r') as fh:
            self.template = fh.read()


################################################################################
    def _create_html(self):

        # reset week counter on January
        if self.month == 1:
            self.week_number = 0

        tmp = self.template
        tmp = tmp.replace('###month###', '{}'.format(self.month_names[self.month]))
        tmp = tmp.replace('###year###', '{}'.format(self.year))

        month_matrix = calendar.monthcalendar(self.year, self.month)

        inner_html = []
        for week in month_matrix:

            # special case: first calendar week: number 1 is the week containing the first thursday (https://de.wikipedia.org/wiki/Woche#Z.C3.A4hlweise_nach_ISO_8601)
            if self.week_number == 0:
                if week[3] > 0:
                    self.week_number = 1
            # if there is a monday in current week: increment
            elif week[0] > 0:
                self.week_number += 1

            inner_html.append('<tr>')
            inner_html.append('<td><br><br>')
            if self.week_number > 0:
                inner_html.append('{}'.format(self.week_number))  # week number
            inner_html.append('</td>')

            for day in week:
                line = '<td>'
                if day > 0:
                    line += '<div class="inner_head">'
                    line += '{}'.format(day)
                    line += '</div>'

                    cur_date = '{}-{:02d}-{:02d}'.format(self.year, self.month, day)
                    if cur_date in self.data.keys():
                        line += '<div class="inner_content">'
                        tmp_contents = ['<span class="inner_content_marker">{}</span> {}'.format(entry.split(' ')[0], ' '.join(entry.split(' ')[1:])) for entry in self.data[cur_date]]
                        line += '<br>'.join(tmp_contents)
                        line += '</div>'

                line += '</td>'
                inner_html.append(line)

            inner_html.append('</tr>')

        tmp = tmp.replace('###calendar_data###', '\n'.join(inner_html))

        self.html = tmp


################################################################################
    def _write_html(self, filename):
        if not filename.endswith('.htm') or not filename.endswith('.html'):
            filename += '.htm'
        html_dir = os.path.join(self.output_dir, 'html', '{}'.format(self.year))
        os.makedirs(html_dir, exist_ok=True)
        html_file = os.path.join(html_dir, filename)
        with open(html_file, 'w') as fh:
            fh.write(self.html)



################################################################################
################################################################################
class PdfProcessor(BaseProcessor):


################################################################################
    def run(self):

        if not PDFKIT_IMPORTED:
            print()
            print('Error importing pdfkit – cannot create PDF files.')
            print('Try: pip install pdfkit')
            print('Exiting…')
            print()
            sys.exit(1)

        for self.year in (datetime.datetime.now().year, datetime.datetime.now().year + 1):
            for self.month in range(1, 13):
                self._make_pdf_from_html()

            self._concat_year_pdf()


################################################################################
    def _make_pdf_from_html(self):


        html_dir = os.path.join(self.output_dir, 'html', '{}'.format(self.year))
        pdf_dir = os.path.join(self.output_dir, 'pdf', '{}'.format(self.year))
        os.makedirs(pdf_dir, exist_ok=True)

        basename = '{}-{:02d}'.format(self.year, self.month)

        html_file = os.path.join(html_dir, basename + '.htm')
        pdf_file = os.path.join(pdf_dir, basename + '.pdf')

        options = {
            'page-size': 'A4',
            'orientation': 'Landscape',
            'margin-top': '0.7in',
            'margin-right': '0.75in',
            'margin-bottom': '0.7in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8',
        }

        print()
        print('Creating {}'.format(pdf_file))
        pdfkit.from_file(html_file, pdf_file, options=options)


################################################################################
    def _concat_year_pdf(self):

        pdf_dir = os.path.join(self.output_dir, 'pdf', '{}'.format(self.year))

        month_files = []
        for m in range(1, 13):
            filename = '{}-{:02d}.pdf'.format(self.year, m)
            f = os.path.join(pdf_dir, filename)
            month_files.append(f)

        year_file = os.path.join(pdf_dir, '{}.pdf'.format(self.year))

        cmd = 'pdftk {} cat output {}'.format(' '.join(month_files), year_file)

        print()
        print('Calling pdftk: {}'.format(cmd))
        errorcode = subprocess.call(cmd, shell=True)

        if errorcode > 0:
            print('Error {} calling pdftk – could not concat monthly PDF files'.format(errorcode))

        print()




################################################################################
################################################################################
################################################################################
if __name__ == '__main__':


    modes = {
            'base': 'reads the config',
            'bash': 'output to bash',
            'powershell': 'output to powershell',
            'html': 'output to HTML files',
            'pdf': 'output to PDF files (from HTML)',
            }

    usage = [
            '',
            'Usage: {} [{}]'.format(sys.argv[0], '|'.join(sorted(modes.keys()))),
            '',
            ]

    for mode in sorted(modes.items()):
        usage.append('   {}: {}'.format(mode[0], mode[1]))

    if len(sys.argv) != 2 or sys.argv[1] not in modes.keys():
        for l in usage:
            print(l)
        sys.exit(1)

    if sys.argv[1] == 'base':
        processor = BaseProcessor()
        processor.run()
    elif sys.argv[1] == 'bash':
        processor = BashProcessor()
        processor.run()
    elif sys.argv[1] == 'powershell':
        processor = PowershellProcessor()
        processor.run()
    elif sys.argv[1] == 'html':
        processor = HtmlProcessor()
        processor.run()
    elif sys.argv[1] == 'pdf':
        processor = HtmlProcessor()
        processor.run()
        processor = PdfProcessor()
        processor.run()

    # processor.test_output()
