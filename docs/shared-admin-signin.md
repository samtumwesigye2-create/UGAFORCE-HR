# Shared administrator sign-in

UGAFORCE_HR_SHARED_ADMIN_USERNAME binds one administrator username to the Grid master authority. UGAFORCE_HR_SHARED_AUTH_URL must be its HTTPS base URL. The configured username uses the current Grid ADMIN_PASSCODE, verified on each login through POST /vector5250/profiles/bootstrap. Redirects are rejected; outages fail closed with 503. No central password is copied to HR.

After validation, HR issues its normal eight-hour PostgreSQL-backed bearer session. Existing HR roles and account disablement remain enforced. If the configured administrator has no HR record, its first validated login provisions HR_ADMIN with a random unusable local password. Successful sign-ins are audited. Other staff retain their local HR accounts.

This is a master-code bridge, not workforce SSO or MFA. Rotating the central code affects subsequent logins; existing HR sessions keep their normal expiry/revocation rules. A full identity-provider integration is still required for shared individual staff accounts.

Validation: python -m unittest discover -s tests
