# DataAnalysis

DataAnalysis é uma biblioteca que pode ser usada para o pré-processamento de um arquivo csv.

#### Parâmetros:

```diff
input_file: nome do arquivo com a extensão csv

api_small_talks: url da api de small talks

content_column: nome ou índice da coluna de conteúdo do arquivo csv

encoding: codificação do arquivo

sep: separador usado no arquivo

batch: número de batches para usar na api de small talks
```


## Installation

Use o gerenciador de pacotes [pip](https://pip.pypa.io/en/stable/) para instalar o DataAnalysis

```bash
pip install DataAnalysis
```

## Usage

```python
import DataAnalysis as da

p = da.PreProcessing(input_file, api_small_talks, content_column, encoding, sep, batch)
p.process(output_file, lower = True, punctuation = True, abbreviation = True, typo = True, small_talk = True, 
emojis = True, wa_emojis = True, accentuation = True, number = True, relevant = False)
```
## License
[MIT](https://choosealicense.com/licenses/mit/)