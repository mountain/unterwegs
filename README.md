Unterwegs: a personal knowledge tool
====================================

**Unterwegs**, means "on the way" in German language, reflects the nature of knowledge seeking.

the initial idea
------------------

What is an ideal personal knowledge tool?
* there have been a bunch of note-taking tools, but without fulltext searching, easy reference and citation
* there have been several open-sourced searching engines, but are very complex to config and set-up
* there have been many document management tools, but most of them can only manage files not pages or paragraphs

Why it can not integrate all of these handy features in one tool? Maybe it is too heavy for any desktop application.

Then it comes with **Unterwegs**, a personal knowledge tool, running on a Home-NAS or a family server,
which may generally cost you $500 ~ $1000.


the core concept
------------------

Note cards, desktop, library are the core metaphor, and it also featurs
* reading/authoring:
  * text: markdown with math formula support
  * datavis: support vega data visualization
  * references: it can be at article, page and paragraph levels
* organizing
  * classified by category, tag and aspect
* searching
  * fulltext searching
  * search result can be refined into a card with cluster graph and nlp analysis data

For example, the cluster graph of key word "Alan Turing" in my article repository is as below
![Alan Turing](docs/images/alanturing.png?raw=true "Alan Turing")

just on the way
---------------
It is not finished, and is just on the way.

Currently, the main page of the tool is like that:
![computability](docs/images/computability.png?raw=true "computability")

how to run
----------

1. use the docker-compose to setup the system

2. upload pdf files

```bash
curl -v -F upload=@example.pdf http://HOST:PORT/upload
```

3. visting the pages by browser at http://HOST:PORT/

