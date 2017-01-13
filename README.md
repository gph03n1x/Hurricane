## Hurricane

A python search engine + crawler with tornado

### Configuring and Running

Run the following command to install all the packages

```bash
pip install -r requirements.txt
```

Rename the hurricane.cfg.example to hurricane.cfg
and change the settings.

The first time you run it you have to download the
stopwords and punkt nltk packages.

To do that just run it as
```bash
python app.py --update
```

After you download the packages once you don't need
to provide the --update argument anymore except if you
want to update the packages.

```bash
python app.py
```

### Screenshots
[Search page](http://i.imgur.com/F2kgFcA.png)
[Status page](http://i.imgur.com/B9lRyLk.png)

### Frontend
This project uses bootstrap for its frontend
