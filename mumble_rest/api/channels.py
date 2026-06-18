from ninja import Schema
from ..mumble_ice import MumbleServer


class ChannelGroup(Schema):
    name: str
    add: list[int] = []
    remove: list[int] = []
    inherit: bool = True
    inheritable: bool = True


class ChannelData(Schema):
    id: int
    name: str
    parent: int
    description: str = ""
    position: int = 0
    groups: list[ChannelGroup] = []


class ChannelImportRequest(Schema):
    channels: list[ChannelData]


def export_channels(server) -> list[dict]:
    channels = server.getChannels()
    result = []
    for cid, ch in channels.items():
        if ch.temporary:
            continue
        _, groups, _ = server.getACL(cid)
        channel_groups = []
        for g in groups:
            channel_groups.append({
                "name": g.name,
                "add": list(g.add),
                "remove": list(g.remove),
                "inherit": g.inherit,
                "inheritable": g.inheritable,
            })
        result.append({
            "id": ch.id,
            "name": ch.name,
            "parent": ch.parent,
            "description": ch.description or "",
            "position": ch.position,
            "groups": channel_groups,
        })
    return result


def _apply_groups(server, channel_id: int, groups: list[ChannelGroup]):
    acls, existing_groups, inherit = server.getACL(channel_id)
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

    server.setACL(channel_id, acls, existing_groups, inherit)


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
    if root_data and root_data.groups:
        _apply_groups(server, 0, root_data.groups)

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

            if ch.groups:
                _apply_groups(server, new_id, ch.groups)

        remaining = next_remaining

    return id_map
