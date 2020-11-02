# User Stories
### Bitcoin ACKs v1
- [x] As a reviewer I want to see which PRs have “momentum” (concept acks from contributors) so that I can prioritize and best use my review time.
- [x] As a maintainer I want to see which PRs are merge candidates so that I don’t have to wait for authors to ping me or spend time individually analysing PRs.
- [x] As an author I want to see when my PRs are conflicted or not building on Travis so that I can rebase.

### Bitcoin ACKs v2
- [ ] ~As a reviewer I want to see an inter-diff between force-pushed commits so that I can focus on code I have not already reviewed.~ [GitHub implemented this!](https://github.blog/changelog/2018-11-15-force-push-timeline-event/)
- [ ] ~~As an author I want to receive a notification when my PR becomes conflicted so that I can rebase.~~ [DrahtBot](https://github.com/DrahtBot) solves this!
- [ ] ~~As an author, reviewer, or maintainer I want to see which PRs would become conflicted after a PR is merged so that I can coordinate and prioritize.~~  [DrahtBot](https://github.com/DrahtBot) solves this!

### Bitcoin ACKs v3
- [ ] As an author or reviewer I want to have online C++ Jupyter notebooks so that I can explore, reason about, and communicate problems in an interactive manner.



# Contributing


### Using docker-compose for development

- [Install docker-compose](https://docs.docker.com/compose/install/)

- [Create GitHub API token](https://github.com/settings/tokens/new) 
  The token must have the `public_repo` permission scope.

- [Create a GitHub OAuth Application](https://github.com/settings/applications/new)

   For local development set the homepage URL to `http://0.0.0.0:5000/` and 
   set the authorization callback URL to `http://0.0.0.0:5000/login-github/github/authorized`
 
 - [Create Twitter API token](https://developer.twitter.com/en/apps)
 
 
- Add `127.0.0.1 btcpay.local` to [your `/etc/hosts` file](https://www.howtogeek.com/howto/27350/beginner-geek-how-to-edit-your-hosts-file/)
 
- Use the parameters in this repository's `btcpay_dev_env` to [setup a local BTCPay Server](https://github.com/btcpayserver/btcpayserver-docker) 
   
 
- Copy `.env.sample` to `.env` and populate the secrets there

- Run `docker-compose up -d`

- Go to `localhost:5000`
