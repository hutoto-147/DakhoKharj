# Final 1.0.0 audit

- [x] Tested Persian money layout preserved (`٬`, no decimals)
- [x] Splash subtitle preserved; no rotating splash logo
- [x] Backup / Excel / PDF success Toast preserved
- [x] Public applicationId: `io.github.hutoto147.dakhlokharj`
- [x] versionCode 1 / versionName 1.0.0
- [x] Direct SMS permissions and SMS receiver/importer removed
- [x] Notification Access disclosure/consent preserved
- [x] Privacy Policy page included in `docs/`
- [x] Legacy test keystore absent from final source
- [x] Release signing uses environment variables / GitHub Secrets only
- [x] Debug CI covers `release/**`
- [x] Release workflow builds AAB only; no automatic GitHub Release
