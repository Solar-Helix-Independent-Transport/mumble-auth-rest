from ninja import Schema
from ..mumble_ice import MumbleServer


class ChannelGroup(Schema):
    name: str
    inherit: bool = True
    inheritable: bool = True


class ChannelACL(Schema):
    apply_here: bool = True
    apply_subs: bool = True
    group: str = ""
    userid: int = -1
    allow: int = 0
    deny: int = 0


class ChannelData(Schema):
    id: int
    name: str
    parent: int
    description: str = ""
    position: int = 0
    inherit_acls: bool = True
    groups: list[ChannelGroup] = []
    acls: list[ChannelACL] = []


class ChannelImportRequest(Schema):
    channels: list[ChannelData]


def export_channels(server) -> list[dict]:
    channels = server.getChannels()
    result = []
    for cid, ch in channels.items():
        if ch.temporary:
            continue
        acls, groups, inherit_acls = server.getACL(cid)
        channel_groups = []
        for g in groups:
            if g.inherited:
                continue
            channel_groups.append({
                "name": g.name,
                "inherit": g.inherit,
                "inheritable": g.inheritable,
            })
        channel_acls = []
        for a in acls:
            if a.inherited:
                continue
            channel_acls.append({
                "apply_here": a.applyHere,
                "apply_subs": a.applySubs,
                "group": a.group,
                "userid": a.userid,
                "allow": a.allow,
                "deny": a.deny,
            })
        result.append({
            "id": ch.id,
            "name": ch.name,
            "parent": ch.parent,
            "description": ch.description or "",
            "position": ch.position,
            "inherit_acls": inherit_acls,
            "groups": channel_groups,
            "acls": channel_acls,
        })
    return result


def _apply_acls(server, channel_id: int, groups: list[ChannelGroup], acls: list[ChannelACL], inherit_acls: bool):
    _, existing_groups, _ = server.getACL(channel_id)
    existing_by_name = {g.name: g for g in existing_groups}

    for gdata in groups:
        if gdata.name in existing_by_name:
            g = existing_by_name[gdata.name]
        else:
            g = MumbleServer.Group()
            g.name = gdata.name
            existing_groups.append(g)
            existing_by_name[gdata.name] = g

        g.inherit = gdata.inherit
        g.inheritable = gdata.inheritable
        g.add = []
        g.remove = []

    new_acls = []
    for adata in acls:
        a = MumbleServer.ACL()
        a.applyHere = adata.apply_here
        a.applySubs = adata.apply_subs
        a.group = adata.group
        a.userid = adata.userid
        a.allow = adata.allow
        a.deny = adata.deny
        new_acls.append(a)

    server.setACL(channel_id, new_acls, existing_groups, inherit_acls)


def import_channels(server, channels: list[ChannelData]) -> dict:
    # Remove all direct children of root (cascades to their descendants)
    existing = server.getChannels()
    for cid, ch in existing.items():
        if cid != 0 and ch.parent == 0:
            try:
                server.removeChannel(cid)
            except Exception:
                pass

    id_map = {0: 0}

    root_data = next((c for c in channels if c.id == 0), None)
    if root_data:
        _apply_acls(server, 0, root_data.groups, root_data.acls, root_data.inherit_acls)

    # BFS: create channels once their parent is known in id_map
    remaining = [c for c in channels if c.id != 0]
    max_passes = len(remaining) + 1

    for _ in range(max_passes):
        if not remaining:
            break
        next_remaining = []
        for ch in remaining:
            if ch.parent not in id_map:
                next_remaining.append(ch)
                continue

            new_id = server.addChannel(ch.name, id_map[ch.parent])

            state = server.getChannelState(new_id)
            state.description = ch.description
            state.position = ch.position
            server.setChannelState(state)

            id_map[ch.id] = new_id

            _apply_acls(server, new_id, ch.groups, ch.acls, ch.inherit_acls)

        remaining = next_remaining

    return id_map
