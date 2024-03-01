# Earth Analytics Lessons  

This repo contains all of the courses, lessons, workshop materials and blogposts
that support the earthdatascience.org website. Please note that this repo is **private** 
as many of the lessons contain answers to
homework assignment. As such DO NOT FORK this repo!

THe documentation surrounding the CI pipeline attached to this readme is here:
[hack md doc](https://hackmd.io/psb27zRdTHqJfHtNG8kRXw?both)

## Build Environment
We maintain a [DOCKER CONTAINER](https://github.com/earthlab/r-python-eds-lessons-env) 
that controls the build environment in circle ci. If a package is missing, please 
submit a PR to this repo and it will run a test build in dockerhub. If all goes well,
the build will pass and we can merge!

The CI build converts RMD and ipynb files to markdown. It then pushese them to the
[eds-lessons-website repo](https://github.com/earthlab/eds-lessons-website). This 
repo is where all of the images and markdown files are stored that will be pushed 
to our new DRUPAL website when it is live. As a stop gap since we are currently
hosting the site on github, When 
they successfully get to they website repo, they are then pushed via another CI 
pipeline to the live site repo:
[eds-lessons-website repo](https://github.com/earthlab/earthlab.github.io).


## Getting started

To begin clone this repo locally. If you are a Windows user, please read the section
below on long file paths.

### Attention Windows Users - Long File Paths Abound

There are issues with long file paths on windows systems. The fix below should
take care of this issue on your windows machine. Maybe thanks to Gina for
figuring this out AND documenting it here.

WINDOWS: run `git config --system core.longpaths true` to ensure all files are
cloned. Additionally, open the Registry Editor and navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`. Double click
the `LongPathsEnabled` value and change the value from "0" to "1" in the
"Value Data" field and click OK. See full instructions on editing the
registry [here](https://www.howtogeek.com/266621/how-to-make-windows-10-accept-file-paths-over-260-characters/).

Next clone this repository to your local machine. Do so by running:

```
# clone the repository, , make the site, and serve it.
git clone $(The repo's URL)

cd $(The repo you just cloned)
```
The environment that is being used to build these lessons lives here: 

https://github.com/earthlab/r-python-eds-lessons-env

Feel free to pull that docker container from dockerhub to grab it and build locally if you'd like!

