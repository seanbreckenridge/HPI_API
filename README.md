An automatic JSON API for [HPI](https://github.com/karlicoss/HPI)

This inspects functions in each `HPI` module file, generating routes for each of them.

This provides access to the data fine, but I wouldn't recommend putting this up on the public internet as this allows anything that can make a GET request to call arbitrary functions in HPI; At least put it behind some authenticated proxy or host it on a private port

If you have any suggestions/trouble with getting this to work, feel free to open an Issue/PR!

---

### Installation

Requires `python3.7+`

To install with pip, run:

    pip install git+https://github.com/seanbreckenridge/HPI_API

---

### Usage

For each function in an HPI module, this generates a HTTP route. For example, if you had the module `my.reddit`, which had a function `comments`, which returned an iterator/list of your `reddit` comments, requesting `/my/reddit/comments` will call that function.

- If the function fails to be called, it returns an HTTP code > 400.
- If the function succeeds
  - and this returns a primitive, a `dict` or this is the stats function, it returns the value directly
  - otherwise, this assumes its returning some iterable event-like response, and the following GET parameters let you paginate:
    - limit: int (defaults to 50)
    - page: int (defaults to 1)

Theres no limit to the `limit` param, if you wanted to grab all the data, you can always do something like `?limit=99999999999999999&page=1`

Though I'm not a huge fan of pagination, the `limit` included anyways. Otherwise, if not behind `cachew`, some responses may take a _long_ time to compute

After installing, you can run this server with:

```bash
$ python3 -m my_api server  # or `hpi_api server`
```

To list the routes, you can run one of the following:

```bash
$ curl 'localhost:5050/routes'
$ hpi_api list-modules --functions
$ hpi_api sever --print-routes
```

Here are some examples:

```bash
$ curl 'localhost:5050/my/zsh/history?limit=3'
{"items":[{"command":"z","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0},{"command":"en env_config.zsh","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0},{"command":"ls","dt":"Mon, 18 May 2020 08:23:22 GMT","duration":0}],"limit":3,"page":1}
$ curl 'localhost:5050/my/github/all/events?limit=1' | jq -r '.items | .[0]'
{
  "body": "Note: This is used for [gitopen](https://github.com/seanbreckenridge/dotfiles/commit/4c57fd97cbb2605e63d0cf5d2af37039fe6e6d35)",
  "dt": "Thu, 14 Feb 2019 21:05:40 GMT",
  "eid": "commoit_comment_https://github.com/seanbreckenridge/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943",
  "is_bot": false,
  "link": "https://github.com/seanbreckenridge/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943",
  "summary": "commented on https://github.com/seanbreckenridge/mac-dotfiles/commit/d4ac3c30dd3df1b626f92eb61f651a27852ff86f#commitcomment-32324943"
}
$ curl localhost:5050/my/zsh/stats
{"value":{"history":{"count":266722}}}
```
