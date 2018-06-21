from marshmallow import Schema, fields


class ProjectSchema(Schema):
    id = fields.Str()
    number = fields.Int()
    state = fields.Str()


class ProjectColumnSchema(Schema):
    id = fields.Str()
    name = fields.Str()


class ProjectCardSchema(Schema):
    id = fields.Str()
    column = fields.Nested(ProjectColumnSchema, allow_none=True)
    project = fields.Nested(ProjectSchema)
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime()


class ProjectCardsSchema(Schema):
    nodes = fields.Nested(ProjectCardSchema, many=True, allow_none=True)
    totalCount = fields.Int()
