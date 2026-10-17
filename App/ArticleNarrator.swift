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
        if key.contains("zh-cn.lilian") { return "黎潋" }
        if key.contains("zh-cn.han") { return "瀚" }
        if key.contains("li-mu") || key.contains("limu") { return "李沐" }
        if key.contains("yu-shu") || key.contains("yushu") { return "语舒" }
        return gender == .male ? "普通话男声" : "普通话女声"
    }
    var character: String {
        if displayName == "瀚" { return "沉稳男声" }
        if displayName == "黎潋" { return "自然女声" }
        if displayName == "李沐" { return "沉稳男声" }
        if displayName == "语舒" { return "自然女声" }
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
final class ArticleNarrator: NSObject, ObservableObject, AVSpeechSynthesizerDelegate, AVAudioPlayerDelegate {
    private static let voicePreviewText = "康熙六十一年，康熙帝去世，皇四子胤禛继位，是为雍正帝。雍正十三年，皇四子弘历即位，次年改元乾隆。制度的延续与调整，也由此进入新的阶段。"
    @Published private(set) var isSpeaking = false
    @Published private(set) var isPaused = false
    @Published private(set) var isLoading = false
    @Published private(set) var elapsed: TimeInterval = 0
    @Published private(set) var duration: TimeInterval = 0
    @Published private(set) var currentSectionID: String?
    @Published private(set) var currentTitle = ""
    @Published private(set) var currentIndex = 0
    @Published private(set) var sectionCount = 0
    @Published var speed: NarrationSpeed
    @Published private(set) var voices: [NarrationVoiceOption]
    @Published private(set) var selectedVoiceID: String
    let dynastyID: String

    private let synthesizer = AVSpeechSynthesizer()
    private let previewSynthesizer = AVSpeechSynthesizer()
    private var audioPlayer: AVAudioPlayer?
    private var loadingTask: Task<Void, Never>?
    private var progressTimer: Timer?
    private var sections: [ArticleSection] = []
    private var autoAdvanceEnabled = false
    // Ignore delegate callbacks from an utterance replaced by navigation or settings.
    private var activeUtteranceID: ObjectIdentifier?
    private var previewUtteranceID: ObjectIdentifier?
    private var restartOnResume = false
    @Published private(set) var previewVoiceID: String?

    init(dynastyID: String = "") {
        self.dynastyID = dynastyID
        let available = Self.installedChineseVoices()
        voices = available
        let saved = UserDefaults.standard.string(forKey: "narrationVoiceV2")
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

    var isActive: Bool { isSpeaking || isPaused || isLoading }
    var usesDoubaoNarration: Bool { dynastyID == "ming" || dynastyID == "qing" }
    private var shouldLoadRecordedNarration: Bool { usesDoubaoNarration }
    var canSeek: Bool { audioPlayer != nil && duration > 0 }
    var canGoPrevious: Bool { isActive && currentIndex > 0 }
    var canGoNext: Bool { isActive && currentIndex + 1 < sectionCount }

    func toggle(article: Article, from sectionID: String?) {
        guard usesDoubaoNarration || !voices.isEmpty else { return }
        stopPreview()
        if isLoading {
            stop()
        } else if isPaused {
            if restartOnResume {
                speakCurrentSection()
            } else if let audioPlayer {
                audioPlayer.play()
                isPaused = false
                isSpeaking = true
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
        guard isSpeaking else { return }
        if let audioPlayer, audioPlayer.isPlaying {
            audioPlayer.pause()
        } else if !synthesizer.pauseSpeaking(at: .immediate) {
            return
        }
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
        sectionsArticleID = article.id
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
        if let audioPlayer, isActive {
            audioPlayer.rate = newSpeed.audioRate
            return
        }
        guard isActive else { return }
        move(to: currentIndex)
    }

    func changeVoice(_ identifier: String) {
        guard identifier != selectedVoiceID, voices.contains(where: { $0.id == identifier }) else { return }
        selectedVoiceID = identifier
        UserDefaults.standard.set(identifier, forKey: "narrationVoiceV2")
        guard isActive, audioPlayer == nil else { return }
        move(to: currentIndex)
    }

    func seek(to time: TimeInterval) {
        guard let audioPlayer, audioPlayer.duration > 0 else { return }
        let target = min(max(0, time), audioPlayer.duration)
        audioPlayer.currentTime = target
        elapsed = target
    }

    func preview(_ option: NarrationVoiceOption) {
        stopPreview()
        pause()
        configureAudioSession()
        let utterance = AVSpeechUtterance(string: Self.voicePreviewText)
        utterance.voice = AVSpeechSynthesisVoice(identifier: option.id)
        utterance.rate = 0.45
        utterance.pitchMultiplier = 1.0
        utterance.prefersAssistiveTechnologySettings = false
        utterance.preUtteranceDelay = 0.08
        utterance.postUtteranceDelay = 0.1
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
        loadingTask?.cancel()
        loadingTask = nil
        stopProgressTimer()
        audioPlayer?.stop()
        audioPlayer = nil
        elapsed = 0
        duration = 0
        activeUtteranceID = nil
        restartOnResume = false
        synthesizer.stopSpeaking(at: .immediate)
        stopPreview()
        isSpeaking = false
        isPaused = false
        isLoading = false
        currentSectionID = nil
        currentTitle = ""
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
    }

    private func move(to index: Int) {
        guard sections.indices.contains(index) else { return }
        stopPreview()
        let keepPaused = isPaused
        loadingTask?.cancel()
        loadingTask = nil
        stopProgressTimer()
        audioPlayer?.stop()
        audioPlayer = nil
        elapsed = 0
        duration = 0
        isLoading = false
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
        guard sections.indices.contains(currentIndex) else {
            stop()
            return
        }
        restartOnResume = false
        let section = sections[currentIndex]
        currentSectionID = section.id
        currentTitle = section.title
        isPaused = false

        if shouldLoadRecordedNarration,
           let manifest = NarrationAudioManifest.bundled,
           let entry = manifest.entry(articleID: sectionsArticleID, section: section) {
            loadDoubaoAudio(entry: entry, manifest: manifest)
            return
        }
        speakSystemSection(section)
    }

    private var sectionsArticleID = ""

    private func loadDoubaoAudio(entry: NarrationAudioManifest.Entry, manifest: NarrationAudioManifest) {
        isLoading = true
        isSpeaking = false
        configureAudioSession()
        loadingTask = Task { [weak self] in
            guard let self else { return }
            do {
                let file = try await NarrationAudioCache.shared.localFile(for: entry, manifest: manifest)
                try Task.checkCancellation()
                guard self.sections.indices.contains(self.currentIndex), self.sections[self.currentIndex].id == entry.sectionID else { return }
                let player = try AVAudioPlayer(contentsOf: file)
                player.delegate = self
                player.enableRate = true
                player.rate = self.speed.audioRate
                player.prepareToPlay()
                self.audioPlayer = player
                self.elapsed = player.currentTime
                self.duration = player.duration
                self.startProgressTimer()
                self.isLoading = false
                self.isSpeaking = player.play()
                if !self.isSpeaking { self.speakSystemSection(self.sections[self.currentIndex]) }
            } catch is CancellationError {
                return
            } catch {
                guard self.sections.indices.contains(self.currentIndex), self.sections[self.currentIndex].id == entry.sectionID else { return }
                self.speakSystemSection(self.sections[self.currentIndex])
            }
        }
    }

    private func speakSystemSection(_ section: ArticleSection) {
        stopProgressTimer()
        elapsed = 0
        duration = 0
        isLoading = false
        loadingTask = nil
        audioPlayer = nil
        guard let voice = Self.mandarinVoice(identifier: selectedVoiceID) else {
            stop()
            return
        }
        isSpeaking = true

        configureAudioSession()

        let utterance = AVSpeechUtterance(string: Self.spokenText(for: section))
        utterance.voice = voice
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

    private func startProgressTimer() {
        stopProgressTimer()
        let timer = Timer(timeInterval: 0.25, repeats: true) { [weak self] _ in
            Task { @MainActor [weak self] in
                guard let self, let player = self.audioPlayer else { return }
                self.elapsed = player.currentTime
                self.duration = player.duration
            }
        }
        RunLoop.main.add(timer, forMode: .common)
        progressTimer = timer
    }

    private func stopProgressTimer() {
        progressTimer?.invalidate()
        progressTimer = nil
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

    nonisolated static func spokenText(title: String, text: String) -> String {
        let source = "\(title)。\(text)"
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

    private static func spokenText(for section: ArticleSection) -> String {
        spokenText(title: section.title, text: section.text)
    }

    private static func installedChineseVoices() -> [NarrationVoiceOption] {
        let preferredNames = ["zh-cn.lilian", "zh-cn.han", "yu-shu", "yushu", "li-mu", "limu"]
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
        let order = ["黎潋": 0, "瀚": 1, "语舒": 2, "李沐": 3]
        return bestByName.values.sorted {
            if $0.qualityRank != $1.qualityRank { return $0.qualityRank > $1.qualityRank }
            let left = order[$0.displayName] ?? 99
            let right = order[$1.displayName] ?? 99
            return left < right
        }.prefix(4).map { $0 }
    }

    private static func mandarinVoice(identifier: String) -> AVSpeechSynthesisVoice? {
        if let voice = AVSpeechSynthesisVoice(identifier: identifier),
           voice.language.replacingOccurrences(of: "_", with: "-").lowercased() == "zh-cn",
           !voice.identifier.lowercased().contains("siri") {
            return voice
        }
        return installedChineseVoices().first.flatMap { AVSpeechSynthesisVoice(identifier: $0.id) }
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

    nonisolated func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        let finishedPlayerID = ObjectIdentifier(player)
        Task { @MainActor [weak self] in
            guard let self,
                  let currentPlayer = self.audioPlayer,
                  ObjectIdentifier(currentPlayer) == finishedPlayerID else { return }
            self.audioPlayer = nil
            self.stopProgressTimer()
            self.elapsed = self.duration
            self.finishedSection()
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
    var audioRate: Float {
        switch self {
        case .calm: return 0.85
        case .normal: return 1.0
        case .brisk: return 1.18
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

    private var startingTitle: String {
        article.sections.first(where: { $0.id == visibleSectionID })?.title ?? article.sections.first?.title ?? ""
    }

    var body: some View {
        VStack(spacing: 0) {
            Rectangle().fill(Theme.line.opacity(0.75)).frame(height: 0.5)
            if narrator.canSeek {
                HStack(spacing: 12) {
                    Text(timeLabel(narrator.elapsed))
                    Slider(
                        value: Binding(get: { narrator.elapsed }, set: { narrator.seek(to: $0) }),
                        in: 0...max(narrator.duration, 0.1)
                    )
                    .tint(Theme.cinnabar)
                    .accessibilityLabel("朗读进度")
                    .accessibilityValue("\(timeLabel(narrator.elapsed))，共 \(timeLabel(narrator.duration))")
                    .accessibilityIdentifier("narrationProgress")
                    Text(timeLabel(narrator.duration))
                }
                .font(.caption.monospacedDigit())
                .foregroundStyle(Theme.muted)
                .padding(.horizontal, 22)
                .padding(.top, 10)
            }
            if typeSize.isAccessibilitySize {
                Text(displayTitle).font(.subheadline).foregroundStyle(Theme.ink)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal, 24).padding(.top, 12)
            }
            HStack(spacing: 8) {
                Button { narrator.toggle(article: article, from: visibleSectionID) } label: {
                    Group {
                        if narrator.isLoading { ProgressView().controlSize(.small) }
                        else { Image(systemName: narrator.isSpeaking ? "pause.fill" : "play.fill").font(.system(size: 15, weight: .semibold)) }
                    }
                    .frame(width: 44, height: 44)
                    .overlay(Circle().stroke(Theme.cinnabar.opacity(0.75), lineWidth: 1))
                }
                .foregroundStyle(Theme.cinnabar)
                .accessibilityLabel(narrator.isLoading ? "取消载入" : (narrator.isSpeaking ? "暂停朗读" : (narrator.isPaused ? "继续朗读" : "开始朗读")))
                .accessibilityIdentifier("narrationToggle")
                .accessibilityValue(narrator.isActive ? narrator.currentTitle : startingTitle)

                if !typeSize.isAccessibilitySize {
                VStack(alignment: .leading, spacing: 3) {
                    Text("朗读").font(.caption).foregroundStyle(Theme.cinnabar)
                    Text(displayTitle).font(.subheadline).foregroundStyle(Theme.ink).lineLimit(1)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                } else { Spacer(minLength: 0) }

                Button { narrator.previous() } label: {
                    Image(systemName: "backward.end").font(.system(size: 17, weight: .medium)).frame(width: 44, height: 44)
                }
                .disabled(!narrator.canGoPrevious)
                .foregroundStyle(narrator.canGoPrevious ? Theme.ink : Theme.muted.opacity(0.35))
                .accessibilityLabel("上一节")
                .accessibilityIdentifier("narrationPrevious")

                Button { narrator.next() } label: {
                    Image(systemName: "forward.end").font(.system(size: 17, weight: .medium)).frame(width: 44, height: 44)
                }
                .disabled(!narrator.canGoNext)
                .foregroundStyle(narrator.canGoNext ? Theme.ink : Theme.muted.opacity(0.35))
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
        .background(Theme.paper)
        .foregroundStyle(Theme.ink)
        .sheet(isPresented: $showingSettings) {
            NarrationSettingsSheet(narrator: narrator)
                .presentationDetents([.medium, .large])
                .presentationDragIndicator(.visible)
        }
    }

    private func timeLabel(_ interval: TimeInterval) -> String {
        guard interval.isFinite, interval >= 0 else { return "0:00" }
        let total = Int(interval.rounded(.down))
        return String(format: "%d:%02d", total / 60, total % 60)
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
                    if !narrator.usesDoubaoNarration {
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
                        Text("每个试听使用同一段历史正文。这里只显示设备已经安装的中国大陆普通话声音。")
                            .font(.caption).foregroundStyle(Theme.muted).lineSpacing(4)
                    }
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
