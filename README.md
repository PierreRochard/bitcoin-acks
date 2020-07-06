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

- Copy `dotenv` to `.env` and populate the secrets there

- Run `docker-compose up -d`

- Go to `localhost:5000`
