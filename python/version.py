from git import Repo

def getVersion(path=''):
    r = Repo(path, search_parent_directories=True)
    tags = sorted(repo.tags, key=lambda t: t.tag.tagged_date)
    tag = tags[-1]
    commit = str(r.commit('HEAD'))
    return f"{tag} ({commit})"