# adaboost

Implementation of adaboost algorithm to classify gender,
based on comments from instagram media(s).

## Setup

Assuming you have `virtualenv` installed:
- `virtualenv venv && source venv/bin/activate`
- `pip install -r requirements.txt`
- `./ada.py --help`

```
$ ./ada.py -h
usage: ada.py [-h] [-l LIMIT] [-r MALE_FEMALE_RATIO] [-c] [-g GAMMA]
              [-k KERNEL]

optional arguments:
  -h, --help            show this help message and exit
  -l LIMIT, --limit LIMIT
                        Limit processed data, default ratio is equal male and
                        female comments
  -r MALE_FEMALE_RATIO, --male-female-ratio MALE_FEMALE_RATIO
                        Male to female ratio
  -c, --cache           Cache processed raw data
  -g GAMMA, --gamma GAMMA
                        Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’
  -k KERNEL, --kernel KERNEL
                        Specifies the kernel type to be used in the algorithm
```

- `deactivate`

## Words Blacklist

Put blacklisted words in `data/blacklist.txt` (one word per line)

They will be read at the beginning of the program.

## Example

```
$ ./ada.py -l 2000 -r 0.3
Running AdaBoost Classifier
Reading blacklist words file
Reading raw gender-comment data
Loaded 23499 male and 51030 female comments
Limiting male and female comments to 600 male and 1400 female (2000 total)
Total of 5162 words found

Processing 2000 raw gender-comment data: [#######################################-]

Running tests
=============
Test-1
> Training model...
> Predicting test data...
> Accuracy: 68.80%

Test-2
> Training model...
> Predicting test data...
> Accuracy: 70.40%

Test-3
> Training model...
> Predicting test data...
> Accuracy: 74.40%

Test-4
> Training model...
> Predicting test data...
> Accuracy: 70.80%

Test-5
> Training model...
> Predicting test data...
> Accuracy: 70.00%

Test-6
> Training model...
> Predicting test data...
> Accuracy: 66.40%

Test-7
> Training model...
> Predicting test data...
> Accuracy: 68.80%

Test-8
> Training model...
> Predicting test data...
> Accuracy: 71.60%

=====================================
Avg. Accuracy: 70.15%
Elapsed time: 278.01s
```

## Reference

`https://scikit-learn.org/stable/modules/ensemble.html#adaboost`