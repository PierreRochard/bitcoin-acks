from marshmallow import Schema, fields


class AuthorSchema(Schema):
    avatarUrl = fields.Url()
    login = fields.Str()
    url = fields.Url()


class CommentSchema(Schema):
    author = fields.Nested(AuthorSchema)
    body = fields.Str()
    id = fields.Str()
    publishedAt = fields.DateTime()
    url = fields.Url()


class CommentsSchema(Schema):
    nodes = fields.Nested(CommentSchema, many=True)
    totalCount = fields.Int()


class StatusContextSchema(Schema):
    description = fields.Str()


class StatusSchema(Schema):
    contexts = fields.Nested(StatusContextSchema, many=True)
    state = fields.Str()


class CommitSchema(Schema):
    oid = fields.Str()
    status = fields.Nested(StatusSchema)


class PullRequestCommitSchema(Schema):
    commit = fields.Nested(CommitSchema)


class PullRequestCommitsSchema(Schema):
    nodes = fields.Nested(PullRequestCommitSchema, many=True)
    totalCount = fields.Int()


class LabelSchema(Schema):
    color = fields.Str()
    id = fields.Str()
    name = fields.Str()


class LabelsSchema(Schema):
    nodes = fields.Nested(LabelSchema, many=True)
    totalCount = fields.Int()


class PullRequestSchema(Schema):
    additions = fields.Int()
    author = fields.Nested(AuthorSchema)
    bodyHTML = fields.Str()
    closedAt = fields.DateTime(allow_none=True)
    comments = fields.Nested(CommentsSchema)
    commits = fields.Nested(PullRequestCommitsSchema)
    createdAt = fields.DateTime()
    deletions = fields.Int()
    id = fields.Str()
    labels = fields.Nested(LabelsSchema)
    mergeable = fields.Str()
    mergedAt = fields.DateTime(allow_none=True)
    number = fields.Int()
    state = fields.Str()
    title = fields.Str()
    updatedAt = fields.DateTime()
