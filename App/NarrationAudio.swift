import AVFoundation
import CryptoKit
import Foundation

struct NarrationAudioManifest: Decodable {
    struct Entry: Decodable {
        let articleID: String
        let sectionID: String
        let path: String
        let textHash: String
        let audioHash: String?
    }

    let version: Int
    let voiceName: String
    let published: Bool
    let baseURL: String
    let entries: [Entry]

    static let bundled: NarrationAudioManifest? = {
        guard let url = Bundle.main.url(forResource: "narration_manifest", withExtension: "json"),
              let data = try? Data(contentsOf: url) else { return nil }
        return try? JSONDecoder().decode(NarrationAudioManifest.self, from: data)
    }()

    func entry(articleID: String, section: ArticleSection) -> Entry? {
        guard published else { return nil }
        let expectedHash = Self.textHash(title: section.title, text: section.text)
        return entries.first {
            $0.articleID == articleID && $0.sectionID == section.id && $0.textHash == expectedHash
        }
    }

    func remoteURL(for entry: Entry) -> URL? {
        guard var base = URL(string: baseURL) else { return nil }
        base.append(path: entry.path)
        return base
    }

    func bundledURL(for entry: Entry) -> URL? {
        let filename = entry.path as NSString
        let stem = filename.deletingPathExtension
        let ext = filename.pathExtension
        return Bundle.main.url(forResource: stem, withExtension: ext)
            ?? Bundle.main.url(forResource: stem, withExtension: ext, subdirectory: "NarrationAudio")
    }

    static func textHash(title: String, text: String) -> String {
        let spoken = ArticleNarrator.spokenText(title: title, text: text)
        return SHA256.hash(data: Data(spoken.utf8)).map { String(format: "%02x", $0) }.joined()
    }
}

actor NarrationAudioCache {
    static let shared = NarrationAudioCache()

    enum CacheError: Error { case unavailable, invalidResponse }

    func localFile(for entry: NarrationAudioManifest.Entry, manifest: NarrationAudioManifest) async throws -> URL {
        if let bundled = manifest.bundledURL(for: entry),
           isUsableAudio(at: bundled, expectedHash: entry.audioHash) {
            return bundled
        }
        guard let remoteURL = manifest.remoteURL(for: entry) else { throw CacheError.unavailable }
        let manager = FileManager.default
        let root = try manager.url(for: .cachesDirectory, in: .userDomainMask, appropriateFor: nil, create: true)
            .appending(path: "NarrationAudio/v\(manifest.version)", directoryHint: .isDirectory)
        try manager.createDirectory(at: root, withIntermediateDirectories: true)
        let destination = root.appending(path: entry.path)
        if manager.fileExists(atPath: destination.path) {
            if isUsableAudio(at: destination, expectedHash: entry.audioHash) { return destination }
            try? manager.removeItem(at: destination)
        }

        let (temporary, response) = try await URLSession.shared.download(from: remoteURL)
        guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
            throw CacheError.invalidResponse
        }
        try manager.createDirectory(at: destination.deletingLastPathComponent(), withIntermediateDirectories: true)
        let staged = destination.appendingPathExtension("download")
        try? manager.removeItem(at: staged)
        try manager.moveItem(at: temporary, to: staged)
        guard isUsableAudio(at: staged, expectedHash: entry.audioHash) else {
            try? manager.removeItem(at: staged)
            throw CacheError.invalidResponse
        }
        try? manager.removeItem(at: destination)
        try manager.moveItem(at: staged, to: destination)
        return destination
    }

    private func isUsableAudio(at url: URL, expectedHash: String?) -> Bool {
        let manager = FileManager.default
        let size = (try? manager.attributesOfItem(atPath: url.path)[.size] as? NSNumber)?.intValue ?? 0
        guard size > 1_024, let handle = try? FileHandle(forReadingFrom: url) else { return false }
        let header = handle.readData(ofLength: 3)
        try? handle.close()
        guard header.count >= 2 else { return false }
        guard header.starts(with: Data("ID3".utf8)) || (header[0] == 0xff && header[1] & 0xe0 == 0xe0) else {
            return false
        }
        guard let expectedHash else { return true }
        guard let data = try? Data(contentsOf: url, options: .mappedIfSafe) else { return false }
        let actualHash = SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
        return actualHash == expectedHash
    }
}
