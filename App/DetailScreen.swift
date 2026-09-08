import SwiftUI

struct DetailScreen: View {
    let route: DetailRoute
    let store: HistoryStore
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 26) {
                switch route {
                case .event(let id): if let e = store.content.events.first(where: { $0.id == id }) { eventContent(e) }
                case .object(let id): if let o = store.content.objects.first(where: { $0.id == id }) { objectContent(o) }
                case .tomb(let id): if let t = store.content.tombs?.first(where: { $0.id == id }) { tombContent(t) }
                case .about: about
                default: EmptyView()
                }
            }.frame(maxWidth: .infinity, alignment: .leading).padding(24).padding(.bottom, 20)
        }.background(Theme.paper).foregroundStyle(Theme.text).navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
    }
    func title(_ eyebrow: String, _ text: String) -> some View {
        VStack(alignment: .leading, spacing: 9) { Text(eyebrow).font(.caption).foregroundStyle(Theme.cinnabar); Text(text).font(.system(.largeTitle, design: .serif).weight(.medium)).foregroundStyle(Theme.ink).fixedSize(horizontal: false, vertical: true) }
    }
    func block(_ heading: String, _ text: String) -> some View {
        VStack(alignment: .leading, spacing: 12) { sectionTitle(heading); Text(text).font(.body).lineSpacing(6).fixedSize(horizontal: false, vertical: true) }
    }
    func meta(_ key: String, _ value: String) -> some View { VStack(alignment: .leading, spacing: 5) { Text(key).font(.caption).foregroundStyle(Theme.muted); Text(value).font(.body).fixedSize(horizontal: false, vertical: true) } }
    func eventContent(_ e: HistoryEvent) -> some View {
        Group {
            title(e.year, e.title)
            block("发生了什么", e.body)
            block("改变与影响", e.impact)
            linkedPeople(e.people, roles: e.peopleRoles)
            ForEach(e.people, id: \.self) { id in if let a = store.article(id) { NavigationLink("延伸阅读　\(a.title)", value: DetailRoute.article(id)).font(.subheadline).frame(minHeight: 44) } }
            SourcesView(store: store, ids: e.sources)
        }
    }
    func objectContent(_ o: Artifact) -> some View {
        Group {
            title(o.collectionCategory.title, o.title)
            if let image = o.image { LocalImage(name: image).frame(maxWidth: .infinity).frame(height: 290).accessibilityLabel(o.title) }
            Text(o.subtitle).font(.headline).foregroundStyle(Theme.muted)
            Text(o.body).lineSpacing(6)
            block(o.collectionCategory.detailNoteTitle, o.note)
            linkedPeople(o.people)
            SourcesView(store: store, ids: o.sources)
        }
    }
    func tombContent(_ t: Tomb) -> some View {
        Group {
            title(store.person(t.person).call, t.title)
            VStack(alignment: .leading, spacing: 18) { meta("陵区", t.area); meta("所在地", t.location); meta("安葬信息", t.status) }
            block("陵寝与历史", t.body)
            if !t.note.isEmpty { Text(t.note).font(.subheadline).foregroundStyle(Theme.muted).lineSpacing(5) }
            linkedPeople([t.person])
            if let article = store.article(t.person) { NavigationLink(article.title, value: DetailRoute.article(t.person)).frame(minHeight: 44) }
            SourcesView(store: store, ids: t.sources)
        }
    }
    func linkedPeople(_ ids: [String], roles: [String: String]? = nil) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionTitle("从人物继续探索")
            ForEach(ids, id: \.self) { id in
                NavigationLink(value: store.person(id).kind == "皇帝" ? DetailRoute.family(id) : DetailRoute.person(id)) {
                    HStack { Text(store.person(id).name); Spacer(); Text(roles?[id] ?? (store.person(id).kind == "皇帝" ? "家族" : "人物")).font(.caption).foregroundStyle(Theme.muted) }.frame(minHeight: 52).contentShape(Rectangle())
                }.buttonStyle(QuietRowStyle()).accessibilityIdentifier("explore_\(id)")
            }
        }
    }
    var about: some View {
        Group {
            title("关于", "史迹")
            Text("在朝代、帝序、家族与遗珍之间，读懂人物与时代。").font(.title3)
            block("资料", "正文依据史料与馆藏资料整理，各节附有出处；争议记载另作说明。")
            block("阅读", "文章与图片可离线查看；外部出处需要联网。阅读进度仅保存在本机。")
        }
    }

}
struct SourcesView: View {
    let store: HistoryStore
    let ids: [String]
    var compact = false
    var body: some View {
        if compact {
            entries(numbered: false)
        } else {
            VStack(alignment: .leading, spacing: 16) {
                Divider()
                DisclosureGroup("资料与出处") { entries(numbered: true).padding(.top, 12) }
                    .font(.subheadline).tint(Theme.muted)
            }
        }
    }
    private var uniqueIDs: [String] {
        ids.reduce(into: []) { result, id in
            if !result.contains(id) { result.append(id) }
        }
    }
    private func entries(numbered: Bool) -> some View {
        VStack(alignment: .leading, spacing: 0) {
            ForEach(Array(uniqueIDs.enumerated()), id: \.element) { index, id in
                if let source = store.content.sources.first(where: { $0.id == id }), let url = URL(string: source.url) {
                    HStack(alignment: .top, spacing: numbered ? 14 : 0) {
                        if numbered {
                            Text(String(format: "%02d", index + 1))
                                .font(.caption2.monospacedDigit().weight(.medium))
                                .foregroundStyle(Theme.cinnabar)
                                .frame(width: 24, alignment: .leading)
                                .padding(.top, 3)
                                .accessibilityHidden(true)
                        }
                        VStack(alignment: .leading, spacing: 6) {
                            Link(source.title, destination: url)
                                .font(.subheadline)
                                .multilineTextAlignment(.leading)
                                .frame(maxWidth: .infinity, minHeight: 36, alignment: .leading)
                                .accessibilityHint("在浏览器中打开原始出处")
                                .accessibilityIdentifier("source_\(id)")
                            if !source.note.isEmpty {
                                Text(source.note).font(.caption).foregroundStyle(Theme.muted)
                                    .multilineTextAlignment(.leading)
                                    .fixedSize(horizontal: false, vertical: true)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.vertical, 10)
                    if index < uniqueIDs.count - 1 { Rectangle().fill(Theme.line.opacity(0.4)).frame(height: 0.5) }
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
