[![Travis build](https://secure.travis-ci.org/jplusplus/detective.io.png?branch=master)](https://travis-ci.org/jplusplus/detective.io)
[![Coverage Status - master](https://coveralls.io/repos/jplusplus/detective.io/badge.png)](https://coveralls.io/r/jplusplus/detective.io)
(develop branch covergage: [![Coverage Status - develop](https://coveralls.io/repos/jplusplus/detective.io/badge.png?branch=develop)](https://coveralls.io/r/jplusplus/detective.io?branch=develop))

## Installation

**1. Prerequisite**
```bash
sudo apt-get install build-essential git-core python python-pip python-dev libmemcached-dev
sudo pip install virtualenv
```

**2.  Download the project**
```bash
git clone git@github.com:jplusplus/detective.io.git
cd detective.io
```

**3. Install**
```bash
make install
```

## Run in development
```bash
make run
```

Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## License

This software is under the [GNU GENERAL PUBLIC LICENSE v3](./LICENSE).
