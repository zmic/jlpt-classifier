import json
import os
import zipfile

# https://stackoverflow.com/a/48374671/89373
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plot
import requests


JMDICT_JSON_URL = 'https://github.com/scriptin/jmdict-simplified/releases/download/2.0.0/jmdict_eng.json.zip'
JLPT_COLORS = {
    1: '#d84c43',
    2: '#f6934b',
    3: '#dd9f40',
    4: '#48a17a',
    5: '#5890c5',
}


def _make_build_dir():
    if not os.path.exists('build'):
        os.makedirs('build')




def _get_word_frequencies():
    '''
    Maps word to (frequency_ordinal, frequency) in corpus.
    '''
    frequencies = {}
    with open('cb4960_novel_word_freq.txt', 'r') as f:
        for line_number, line in enumerate(f):
            frequency, word, *rest = line.split('\t')
            frequencies[word] = (line_number, frequency)
    return frequencies


def _load_jmdict():
    '''
    Maps JMDict ID to JMDict entry.
    '''
    if not os.path.exists('build/jmdict_eng.json'):
        r = requests.get(JMDICT_JSON_URL, stream=True)
        r.raise_for_status()
        with open('build/jmdict_eng.json.zip', 'wb') as f:
            f.write(r.content)
        zip_ref = zipfile.ZipFile('build/jmdict_eng.json.zip', 'r')
        zip_ref.extractall('build/')
        zip_ref.close()
    with open('build/jmdict_eng.json', 'r') as f:
        jmdict = json.load(f)
    return {entry['id']: entry for entry in jmdict['words']}


def _get_jlpt_lists(jmdict):
    '''
    Maps JLPT level integer to a list of JMDict entries.
    '''
    jlpts = {}
    for level in range(1, 6):
        with open(f'jlpt-n{level}.csv', 'r') as f:
            content = f.readlines()
        items = []
        for line in content:
            if '#' in line:
                continue
            if int(line) not in jmdict:
                print(f'    {int(line)} missing from JMDict; skipping.')
                continue
            items.append(jmdict[int(line)])
        jlpts[level] = items
    return jlpts


def plot_jlpt_list_densities(jlpt_levels, word_frequencies):
    fig, ax = plot.subplots(5, sharex=True)
    #subplot.plot.figure(level_number)
    #ax[-1].set_xlabel('Word Frequency (Highest to Lowest)')
    ax[0].set_title(
        f'Histogram of JLPT Levels Mapped to Word Frequency List')
    ax[0].set_xlim([0, 20000])
    #ax[0].set_ylim([0, 70])
    for (level_number, level_entries) in jlpt_levels.items():
        subplot = ax[level_number - 1]
        subplot.set_ylabel(f'N{level_number}')
        subplot.yaxis.set_visible(False)
        data = set()
        for level_entry in level_entries:
            found_data = None
            for entry_subtype in ['kanji', 'kana']:
                for item in level_entry[entry_subtype]:
                    if item['text'] in word_frequencies:
                        frequency_ordinal, _ = word_frequencies[item['text']]
                        found_data = frequency_ordinal
                        break
                if found_data is not None:
                    break
            if found_data is not None:
                data.add(found_data)

        sorted_data = sorted(list(data))
        n, bins, patches = subplot.hist(
            sorted_data,
            bins=3000,
            density=True,
            histtype='stepfilled',
            color=JLPT_COLORS[level_number])

    plot.show()


def classify():
    _make_build_dir()

    print('Loading JMDict...')
    jmdict = _load_jmdict()

    print('Getting JLPT levels...')
    jlpt_lists = _get_jlpt_lists(jmdict)

    print('Getting Word Frequencies...')
    word_frequencies = _get_word_frequencies()

    print('Plotting JLPT histograms...')
    plot_jlpt_list_densities(jlpt_lists, word_frequencies)


if __name__ == '__main__':
    classify()
