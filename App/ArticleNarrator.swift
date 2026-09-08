import AVFoundation
import SwiftUI

extension Notification.Name {
    static let stopArticleNarration = Notification.Name("stopArticleNarration")
}

struct NarrationVoiceOption: Identifiable, Hashable {
    let id: String
    let name: String
    let language: String
    let qualityRank: Int
    let gender: AVSpeechSynthesisVoiceGender

    init(_ voice: AVSpeechSynthesisVoice) {
        id = voice.identifier
        name = voice.name
        language = voice.language
        qualityRank = voice.quality.rawValue
        gender = voice.gender
    }

    var displayName: String {
        let key = "\(name) \(id)".lowercased()
        if key.contains("li-mu") || key.contains("limu") { return "李沐" }
        if key.contains("yu-shu") || key.contains("yushu") { return "语舒" }
        if key.contains("tingting") || key.contains("ting-ting") { return "婷婷" }
        return gender == .male ? "普通话男声" : "普通话女声"
    }
    var character: String {
        if displayName == "李沐" { return "沉稳男声" }
        if displayName == "语舒" { return "自然女声" }
        if displayName == "婷婷" { return "清晰女声" }
        return gender == .male ? "男声" : "女声"
    }
    var quality: String {
        switch qualityRank {
        case AVSpeechSynthesisVoiceQuality.premium.rawValue: return "高品质"
        case AVSpeechSynthesisVoiceQuality.enhanced.rawValue: return "增强"
        default: return "标准"
        }
    }
}

@MainActor
final class ArticleNarrator: NSObject, ObservableObject, AVSpeechSynthesizerDelegate {
    @Published private(set) var isSpeaking = false
    @Published private(set) var isPaused = false
    @Published private(set) var currentSectionID: String?
    @Published private(set) var currentTitle = ""
    @Published private(set) var currentIndex = 0
    @Published private(set) var sectionCount = 0
    @Published var speed: NarrationSpeed
    @Published private(set) var voices: [NarrationVoiceOption]
    @Published private(set) var selectedVoiceID: String

    private let synthesizer = AVSpeechSynthesizer()
    private let previewSynthesizer = AVSpeechSynthesizer()
    private var sections: [ArticleSection] = []
    private var autoAdvanceEnabled = false
    // Ignore delegate callbacks from an utterance replaced by navigation or settings.
    private var activeUtteranceID: ObjectIdentifier?
    private var previewUtteranceID: ObjectIdentifier?
    private var restartOnResume = false
    @Published private(set) var previewVoiceID: String?

    override init() {
        let available = Self.installedChineseVoices()
        voices = available
        let saved = UserDefaults.standard.string(forKey: "narrationVoice")
        if let saved, available.contains(where: { $0.id == saved }) {
            selectedVoiceID = saved
        } else {
            selectedVoiceID = available.first?.id ?? ""
        }
        speed = NarrationSpeed(rawValue: UserDefaults.standard.string(forKey: "narrationSpeed") ?? "") ?? .normal
        super.init()
        synthesizer.delegate = self
        previewSynthesizer.delegate = self
    }

    var isActive: Bool { isSpeaking || isPaused }
    var canGoPrevious: Bool { isActive && currentIndex > 0 }
    var canGoNext: Bool { isActive && currentIndex + 1 < sectionCount }

    func toggle(article: Article, from sectionID: String?) {
        stopPreview()
        if isPaused {
            if restartOnResume {
                speakCurrentSection()
            } else if synthesizer.continueSpeaking() {
                isPaused = false
                isSpeaking = true
            }
        } else if isSpeaking {
            pause()
        } else {
            start(article: article, from: sectionID)
        }
    }

    private func pause() {
        guard isSpeaking, synthesizer.pauseSpeaking(at: .immediate) else { return }
        isPaused = true
        isSpeaking = false
    }

    func start(article: Article, from sectionID: String?) {
        guard !article.sections.isEmpty else { return }
        stopPreview()
        activeUtteranceID = nil
        synthesizer.stopSpeaking(at: .immediate)
        autoAdvanceEnabled = true
        sections = article.sections
        sectionCount = sections.count
        currentIndex = sectionID.flatMap { id in sections.firstIndex { $0.id == id } } ?? 0
        speakCurrentSection()
    }

    func previous() {
        guard canGoPrevious else { return }
        move(to: currentIndex - 1)
    }

    func next() {
        guard canGoNext else { return }
        move(to: currentIndex + 1)
    }

    func changeSpeed(_ newSpeed: NarrationSpeed) {
        guard speed != newSpeed else { return }
        speed = newSpeed
        UserDefaults.standard.set(newSpeed.rawValue, forKey: "narrationSpeed")
        guard isActive else { return }
        move(to: currentIndex)
    }

    func changeVoice(_ identifier: String) {
        guard identifier != selectedVoiceID, voices.contains(where: { $0.id == identifier }) else { return }
        selectedVoiceID = identifier
        UserDefaults.standard.set(identifier, forKey: "narrationVoice")
        guard isActive else { return }
        move(to: currentIndex)
    }

    func preview(_ option: NarrationVoiceOption) {
        stopPreview()
        pause()
        configureAudioSession()
        let utterance = AVSpeechUtterance(string: "这里是\(option.displayName)，为你朗读中国历史。")
        utterance.voice = AVSpeechSynthesisVoice(identifier: option.id)
        utterance.rate = NarrationSpeed.normal.rate
        previewUtteranceID = ObjectIdentifier(utterance)
        previewVoiceID = option.id
        previewSynthesizer.speak(utterance)
    }

    func stopPreview() {
        previewUtteranceID = nil
        previewVoiceID = nil
        previewSynthesizer.stopSpeaking(at: .immediate)
        if !isActive { try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation) }
    }

    func refreshVoices() {
        let available = Self.installedChineseVoices()
        voices = available
        if !available.contains(where: { $0.id == selectedVoiceID }), let first = available.first {
            selectedVoiceID = first.id
        }
    }

    func stop() {
        autoAdvanceEnabled = false
        activeUtteranceID = nil
        restartOnResume = false
        synthesizer.stopSpeaking(at: .immediate)
        stopPreview()
        isSpeaking = false
        isPaused = false
        currentSectionID = nil
        currentTitle = ""
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    private func move(to index: Int) {
        guard sections.indices.contains(index) else { return }
        stopPreview()
        let keepPaused = isPaused
        activeUtteranceID = nil
        synthesizer.stopSpeaking(at: .immediate)
        currentIndex = index
        if keepPaused {
            restartOnResume = true
            currentSectionID = sections[index].id
            currentTitle = sections[index].title
        } else {
            speakCurrentSection()
        }
    }

    private func speakCurrentSection() {
        guard sections.indices.contains(currentIndex) else { return }
        restartOnResume = false
        let section = sections[currentIndex]
        currentSectionID = section.id
        currentTitle = section.title
        isPaused = false
        isSpeaking = true

        configureAudioSession()

        let utterance = AVSpeechUtterance(string: Self.spokenText(for: section))
        utterance.voice = Self.mandarinVoice(identifier: selectedVoiceID)
        utterance.rate = speed.rate
        utterance.pitchMultiplier = 1.0
        utterance.prefersAssistiveTechnologySettings = false
        utterance.preUtteranceDelay = 0.12
        utterance.postUtteranceDelay = 0.35
        activeUtteranceID = ObjectIdentifier(utterance)
        synthesizer.speak(utterance)
    }

    private func configureAudioSession() {
        let session = AVAudioSession.sharedInstance()
        try? session.setCategory(.playback, mode: .spokenAudio, options: [.duckOthers, .interruptSpokenAudioAndMixWithOthers])
        try? session.setActive(true)
    }

    private func finishedSection() {
        guard autoAdvanceEnabled else { return }
        guard currentIndex + 1 < sections.count else {
            autoAdvanceEnabled = false
            isSpeaking = false
            isPaused = false
            try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
            return
        }
        currentIndex += 1
        speakCurrentSection()
    }

    private static func spokenText(for section: ArticleSection) -> String {
        let source = "\(section.title)。\(section.text)"
        let digits: [Character: Character] = ["0":"零", "1":"一", "2":"二", "3":"三", "4":"四", "5":"五", "6":"六", "7":"七", "8":"八", "9":"九"]
        var result = ""
        var number = ""
        for character in source.replacingOccurrences(of: "—", with: "至") {
            if character.isNumber {
                number.append(character)
                continue
            }
            if character == "年", number.count == 4 {
                result += String(number.map { digits[$0] ?? $0 })
            } else {
                result += number
            }
            number = ""
            result.append(character)
        }
        return result + number
    }

    private static func installedChineseVoices() -> [NarrationVoiceOption] {
        let preferredNames = ["tingting", "ting-ting", "yu-shu", "yushu", "li-mu", "limu"]
        let candidates = AVSpeechSynthesisVoice.speechVoices().filter { voice in
            let language = voice.language.replacingOccurrences(of: "_", with: "-").lowercased()
            let key = "\(voice.name) \(voice.identifier)".lowercased()
            return language == "zh-cn"
                && !key.contains("siri")
                && !key.contains("eloquence")
                && !key.contains("novelty")
                && !key.contains("personal")
                && preferredNames.contains(where: { key.contains($0) })
        }

        var bestByName: [String: NarrationVoiceOption] = [:]
        for voice in candidates.map(NarrationVoiceOption.init) {
            let key = voice.displayName
            if let current = bestByName[key], current.qualityRank >= voice.qualityRank { continue }
            bestByName[key] = voice
        }
        let order = ["婷婷": 0, "语舒": 1, "李沐": 2]
        return bestByName.values.sorted {
            let left = order[$0.displayName] ?? 99
            let right = order[$1.displayName] ?? 99
            if left != right { return left < right }
            return $0.qualityRank > $1.qualityRank
        }.prefix(4).map { $0 }
    }

    private static func mandarinVoice(identifier: String) -> AVSpeechSynthesisVoice? {
        if let voice = AVSpeechSynthesisVoice(identifier: identifier),
           voice.language.replacingOccurrences(of: "_", with: "-").lowercased() == "zh-cn",
           !voice.identifier.lowercased().contains("siri") {
            return voice
        }
        return installedChineseVoices().first.flatMap { AVSpeechSynthesisVoice(identifier: $0.id) }
            ?? AVSpeechSynthesisVoice(language: "zh-CN")
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        let id = ObjectIdentifier(utterance)
        Task { @MainActor [weak self] in
            guard let self else { return }
            if self.previewUtteranceID == id {
                self.stopPreview()
            } else if self.activeUtteranceID == id {
                self.activeUtteranceID = nil
                self.finishedSection()
            }
        }
    }

    nonisolated func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didCancel utterance: AVSpeechUtterance) {
        let id = ObjectIdentifier(utterance)
        Task { @MainActor [weak self] in
            guard let self else { return }
            if self.previewUtteranceID == id { self.stopPreview() }
            if self.activeUtteranceID == id { self.stop() }
        }
    }
}

enum NarrationSpeed: String, CaseIterable, Identifiable {
    case calm = "舒缓"
    case normal = "标准"
    case brisk = "稍快"

    var id: String { rawValue }
    var rate: Float {
        switch self {
        case .calm: return 0.42
        case .normal: return 0.50
        case .brisk: return 0.58
        }
    }
}

struct ArticleNarrationBar: View {
    @Environment(\.dynamicTypeSize) private var typeSize
    let article: Article
    let visibleSectionID: String?
    @ObservedObject var narrator: ArticleNarrator
    @State private var showingSettings = false

    var displayTitle: String {
        narrator.isActive ? narrator.currentTitle : "从当前章节开始"
    }

    var body: some View {
        VStack(spacing: 0) {
            Rectangle().fill(Theme.line.opacity(0.75)).frame(height: 0.5)
            if typeSize.isAccessibilitySize {
                Text(displayTitle).font(.subheadline).foregroundStyle(Theme.ink)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 24).padding(.top, 12)
            }
            HStack(spacing: 8) {
                Button { narrator.toggle(article: article, from: visibleSectionID) } label: {
                    Image(systemName: narrator.isSpeaking ? "pause.fill" : "play.fill")
                        .font(.system(size: 15, weight: .semibold))
                        .frame(width: 44, height: 44)
                        .overlay(Circle().stroke(Theme.cinnabar.opacity(0.75), lineWidth: 1))
                }
                .foregroundStyle(Theme.cinnabar)
                .accessibilityLabel(narrator.isSpeaking ? "暂停朗读" : (narrator.isPaused ? "继续朗读" : "开始朗读"))
                .accessibilityIdentifier("narrationToggle")

                if !typeSize.isAccessibilitySize {
                VStack(alignment: .leading, spacing: 3) {
                    Text("朗读").font(.caption).foregroundStyle(Theme.cinnabar)
                    Text(displayTitle).font(.subheadline).foregroundStyle(Theme.ink).lineLimit(1)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                } else { Spacer(minLength: 0) }

                Button { narrator.previous() } label: {
                    Image(systemName: "backward.end").frame(width: 44, height: 44)
                }
                .disabled(!narrator.canGoPrevious)
                .accessibilityLabel("上一节")
                .accessibilityIdentifier("narrationPrevious")

                Button { narrator.next() } label: {
                    Image(systemName: "forward.end").frame(width: 44, height: 44)
                }
                .disabled(!narrator.canGoNext)
                .accessibilityLabel("下一节")
                .accessibilityIdentifier("narrationNext")

                Button { showingSettings = true } label: {
                    Image(systemName: "slider.horizontal.3")
                        .font(.system(size: 15))
                        .frame(width: 44, height: 44)
                }
                .accessibilityLabel("朗读设置")
                .accessibilityIdentifier("narrationSettings")
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 9)
        }
        .background(Theme.paper.opacity(0.97))
        .foregroundStyle(Theme.ink)
        .sheet(isPresented: $showingSettings) {
            NarrationSettingsSheet(narrator: narrator)
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
        }
    }
}

struct NarrationSettingsSheet: View {
    @ObservedObject var narrator: ArticleNarrator
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 26) {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("语速").font(.system(.title3, design: .serif).weight(.medium))
                        HStack(spacing: 0) {
                            ForEach(NarrationSpeed.allCases) { item in
                                Button { narrator.changeSpeed(item) } label: {
                                    VStack(spacing: 8) {
                                        Text(item.rawValue).font(.subheadline)
                                        Rectangle().fill(narrator.speed == item ? Theme.cinnabar : .clear).frame(width: 24, height: 1.5)
                                    }.frame(maxWidth: .infinity, minHeight: 42).contentShape(Rectangle())
                                }.buttonStyle(.plain).accessibilityIdentifier("narrationSpeed_\(item.rawValue)")
                            }
                        }
                    }
                    VStack(alignment: .leading, spacing: 10) {
                        Text("声音").font(.system(.title3, design: .serif).weight(.medium))
                        ForEach(narrator.voices) { voice in
                            HStack(spacing: 12) {
                                Button { narrator.changeVoice(voice.id) } label: {
                                    HStack(spacing: 12) {
                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(voice.displayName).font(.body).foregroundStyle(Theme.ink)
                                            HStack(spacing: 10) {
                                                Text(voice.character)
                                                Text(voice.quality)
                                            }.font(.caption).foregroundStyle(Theme.muted)
                                        }
                                        Spacer()
                                        if narrator.selectedVoiceID == voice.id { Image(systemName: "checkmark").foregroundStyle(Theme.cinnabar) }
                                    }.frame(minHeight: 52).contentShape(Rectangle())
                                }.buttonStyle(.plain).accessibilityIdentifier("narrationVoice_\(voice.id)")
                                Button {
                                    if narrator.previewVoiceID == voice.id { narrator.stopPreview() }
                                    else { narrator.preview(voice) }
                                } label: {
                                    Image(systemName: narrator.previewVoiceID == voice.id ? "stop.fill" : "speaker.wave.2").frame(width: 44, height: 44)
                                }.buttonStyle(.plain).accessibilityLabel(narrator.previewVoiceID == voice.id ? "停止试听\(voice.displayName)" : "试听\(voice.displayName)")
                                .accessibilityIdentifier("narrationPreview_\(voice.id)")
                            }
                            Rectangle().fill(Theme.line.opacity(0.45)).frame(height: 0.5)
                        }
                        if narrator.voices.isEmpty { Text("未发现可用的中文系统声音").font(.subheadline).foregroundStyle(Theme.muted) }
                        Text("这里只显示设备中已安装的中国大陆普通话声音。需要更多选择，可在系统的中文声音设置中下载语舒或李沐。")
                            .font(.caption).foregroundStyle(Theme.muted).lineSpacing(4)
                    }
                }.padding(24)
            }
            .background(Theme.paper).foregroundStyle(Theme.text)
            .navigationTitle("朗读设置").navigationBarTitleDisplayMode(.inline).toolbarBackground(Theme.paper, for: .navigationBar).toolbarBackground(.visible, for: .navigationBar)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("完成") { dismiss() } } }
            .onAppear { narrator.refreshVoices() }
            .onDisappear { narrator.stopPreview() }
        }
    }
}
