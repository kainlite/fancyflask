# Fancy flask

This is the initial documentation for a default Python application using Flask and Redis,
this should be considered a template for many microservices, etc, it will have a liveness and
readiness probe endpoint as well.

## Pre-requisites

For this to work you need to install:
* [docker](https://www.docker.com/)
* [docker-compose](https://docs.docker.com/compose/)

Instructions vary depending the distribution and operative system, so follow the recommendations by your vendor.

### Local development with docker and docker-compose
From this point you can build the image doing:
```
docker-compose build
```
or
```
docker build . -t flask_app:latest
```
The benefit of using docker-compose is that it will tag the images for you.

### Run
You can run it like this:
```
docker-compose up -d
```

If you need to see the app logs you can do:
```
docker-compose logs -f
```
This will tail the logs of all containers in the manifest.

### Test
To validate that the app works you can do:
```
❯ curl http://0.0.0.0:3000/
Hello from Redis! I have been seen 8 times.
```

There are also some endpoints to check when the pod and or container (depending where it's running)
and the web server are alive and also a readiness endpoint to make sure redis is ok as well,
you can validate those as follows:
Readiness probe:
```
❯ curl http://0.0.0.0:3000/readyz | jq
{
  "status": "All good"
}
```

and for the liveness probe:
```
❯ curl http://0.0.0.0:3000/livez | jq
{
  "status": "IT'S ALIVE!!!"
}
```
You're allowed to laugh at the Frankestein reference :), also note that these endpoints follows
the [kubernetes convention](https://kubernetes.io/docs/reference/using-api/health-checks/) at least in what naming refers.

## Running in kubernetes

To be able to run in kubernetes there is an additional prerequisite, you will need to either install:
* [minikube](https://minikube.sigs.k8s.io/docs/start/)
* [kind](https://kind.sigs.k8s.io/)
* [sops](https://github.com/mozilla/sops)
* [helm](https://helm.sh/docs/intro/install/)
* [helm-secrets](https://github.com/jkroepke/helm-secrets#sops)

Instructions vary depending the distribution and operative system, so follow the recommendations by your vendor.

### Creating and updating secrets
We are going to use an already generated PGP key to create the secrets and I will commit these to the repository so anyone can encrypt/decrypt/test/play.

**Disclaimer**: NEVER DO THIS! Instead use a KMS service from your cloud provider or host your own solution with something
like [Hashicorp Vault](https://www.hashicorp.com/resources/how-vault-compare-cloud-kms)

Import the PGP key:
```
gpg --import pgp/key.asc
```

Encrypt the yaml file:
```
helm secrets enc helm/helm_vars/secrets.yaml
```

Edit/update any secret stored there:
```
helm secrets edit helm/helm_vars/secrets.yaml
```
There are more options like dec and other use cases, I'm keeping it as simple as possible.

### Installing and running
Spin up a local cluster, for example with kind:
```
❯ kind create cluster
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.18.2) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Have a nice day! 👋
```

Then you can deploy the app using the following command:
```
helm dependency update helm/fancyflask
helm secrets upgrade -i fancyflask ./helm/fancyflask -f ./helm/fancyflask/values.yaml -f ./helm/helm_vars/secrets.yaml
```
This command will unwrap secrets and pass them to helm, and then upgrade or install the application and it's dependencies if they are not installed already,
after a few moments you will be able to launch another pod to test (or use port-forwarding), for example:
```
❯ kubectl port-forward svc/fancyflask 3000:80 &
Forwarding from 127.0.0.1:3000 -> 3000

❯ curl localhost:3000
Handling connection for 3000
Hello from Redis! I have been seen 4 times.
```
Note the `&` to run in background.

## Air-gapped environments
If you plan to use this image in an air-gapped environment, meaning isolated from the network and the world, you would need to carry the images in a thumb drive, first export them:
```
docker pull kainlite/fancyflask:latest
docker save kainlite/fancyflask:latest -o fancyflask-latest.tar
```

Then in the secure server do:
```
docker load -i fancyflask-latest.tar
docker tag image_id_from_the_previous_step my.local.registry/fancyflask:latest
docker push my.local.registry/fancyflask:latest
```
The recommended path would be to install a docker registry in the location and use that from the air-gapped environment, for example [portus](http://port.us.org/),
this minimal recommendation assumes that there is already a cluster working and potentially a registry to load the images to.

## Monitoring
Something nice to have would be instrumentation for [prometheus](https://github.com/prometheus/client_python), that way we can store, track and analize metrics later with grafana, it could also be handy to ship logs to an EFK cluster, or use something like datadog or newrelic which already supports all that.

## Notes
On CI and CD: sample github action configured, sadly I don't count with a cluster to deploy and also add the proper config for CD, the image is already being built automatically in [dockerhub](https://hub.docker.com/repository/docker/kainlite/fancyflask).

On the usage of latest: normally I would prefer to use the SHA of the commit given a linear history, but to simplify the example I went with the infamous latest tag.
