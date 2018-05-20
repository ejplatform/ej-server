# Extensions Dockers

This directory contains all compose files from extensions, such as: `rocketchat`.

## Using RocketChat

To deploy the rocketchat local server, you can run its custom docker-compose file:

```bash
sudo docker-compose -f docker/local/start.yml -f docker/extensions/rocketchat.yml
```

To integrate _ej-server_ with this instance of Rocketchat, first you need to get the rocketchat admin user **token**, and **id**. So, first visit `localhost:3000` and create your admin user. For this example, let's treat his name as _rcadmin_. To get his information call the Rocketchat API using curl:

```bash
curl http://localhost:3000/api/v1/login \
     -d "username=rcadmin&password=rcadminpassword"
```

There are other ways to retrieve this data via API. Visit [Rocketchat API docs;](https://rocket.chat/docs/developer-guides/rest-api/authentication/login/).

Now, go to the Rocketchat administration page and setup the [IFrame login integration](https://rocket.chat/docs/developer-guides/iframe-integration/authentication/). Find `Administration > Accounts > IFrame` page. Using _localhost_ it will be `http://localhost:3000/admin/Accounts`.

1. Set `Enabled` option to `True`
2. Enable redirection after success _login_, set `Iframe URL` to `http://localhost:8000/login/?next=/api/v1/rocketchat/redirect`.
3. Rocketchat needs to check if an user is already authenticated. Set `API URL` to `http://localhost:8000/api/v1/rocketchat/check-login`.
4. `API Method` must be `POST`
5. Save changes

You have to modify some Django settings to complete the integration. First go to `Django Admin > Constance (Config) > RocketChat Options`.

* `ROCKETCHAT_URL`: set to the external accessible Rocketchat URL, `http://localhost:3000`.
* `ROCKETCHAT_PRIVATE_URL`: set to the rocketchat docker internal network address `http://rocketchat:3000`, or leave blank if there is no rocketchat private URL.
* `ROCKETCHAT_AUTH_TOKEN`: set to the admin token got on the `curl` command.
* `ROCKETCHAT_USER_ID`: set to the admin ID got on the `curl` command.

Now each time you try to access Rocketchat without django authentication, the user will be redirected to the EJ login page.

Got to `Administration > Layout > Content` and put the content of the main block in rocket-intro.jinja2 file on Layout Home Body.

Get the content of lib/assets/css/rocket.css and put it on custom css section at `Administration > Layout > Custom CSS`
