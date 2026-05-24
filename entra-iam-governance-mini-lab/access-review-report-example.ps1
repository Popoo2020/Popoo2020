# Example PowerShell-style pseudocode for access review reporting
# This is documentation-oriented sample logic, not production code.

$ReviewDate = Get-Date -Format "yyyy-MM-dd"
$Output = @()

$ExampleUsers = @(
    @{ User="alice@example.com"; Role="Employee"; Owner="Line Manager"; LastReview="2026-05-01"; Decision="Keep" },
    @{ User="bob@example.com"; Role="External Consultant"; Owner="Project Owner"; LastReview="2026-04-15"; Decision="Time-limit" },
    @{ User="svc-reporting@example.com"; Role="Service Account"; Owner="Application Owner"; LastReview="2026-03-30"; Decision="Review Required" }
)

foreach ($User in $ExampleUsers) {
    $Output += [PSCustomObject]@{
        ReviewDate = $ReviewDate
        Identity = $User.User
        Role = $User.Role
        AccessOwner = $User.Owner
        LastReview = $User.LastReview
        ReviewDecision = $User.Decision
    }
}

$Output | Format-Table -AutoSize

# In a real environment, this logic would be connected to approved data sources,
# access owner validation and secure evidence storage.
