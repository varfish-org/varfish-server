# Mangement of the GitHub project.

resource "github_repository" "varfish-server" {
  name         = "varfish-server"
  description  = "VarFish: comprehensive DNA variant analysis for diagnostics and research"
  homepage_url = "https://www.cubi.bihealth.org/software/varfish/"
  visibility   = "public"
  topics = [
    "genetics",
    "variant-filtration",
    "variant-priorisation",
    "vcf",
  ]

  has_issues      = true
  has_downloads   = true
  has_discussions = true
  has_projects    = false

  allow_auto_merge   = true
  allow_rebase_merge = false
  allow_merge_commit = false

  delete_branch_on_merge = true

  vulnerability_alerts = true

  squash_merge_commit_message = "BLANK"
  squash_merge_commit_title   = "PR_TITLE"
}
