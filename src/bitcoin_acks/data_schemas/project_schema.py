from marshmallow import Schema, fields


class ProjectSchema(Schema):
    id = fields.Str()
    number = fields.Int()
    title = fields.Str()


class ProjectItemSchema(Schema):
    id = fields.Str()
    project = fields.Nested(ProjectSchema)
    createdAt = fields.DateTime()
    updatedAt = fields.DateTime()
    isArchived = fields.Boolean()


class ProjectItemsSchema(Schema):
    nodes = fields.Nested(ProjectItemSchema, many=True, allow_none=True)
    totalCount = fields.Int()
