import { useEffect, useState } from 'react';
import {
  AlertCircle,
  Check,
  Copy,
  Link2,
  LogOut,
  Plus,
  ShieldCheck,
  UserRound,
  UsersRound,
} from 'lucide-react';
import { authService, familyService } from '../api/services';
import { useFetch } from '../hooks/useFetch';
import { useAuth } from '../context/AuthContext';
import PageHeader from '../components/PageHeader';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import LoadingState from '../components/LoadingState';
import AdvisoryNote from '../components/AdvisoryNote';
import { Spinner } from '../components/LoadingState';
import { formatDate, getErrorMessage, initials } from '../utils/format';

function RoleBadge({ role }) {
  const isAdmin = role === 'admin';
  return (
    <span className={`fs-badge ${isAdmin ? 'bg-emerald-50 text-emerald-700 ring-emerald-200' : 'bg-slate-100 text-slate-600 ring-slate-200'}`}>
      <ShieldCheck className="h-3 w-3" />
      {isAdmin ? 'Admin' : 'Member'}
    </span>
  );
}

async function copyToClipboard(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  const textarea = document.createElement('textarea');
  textarea.value = value;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  const success = document.execCommand('copy');
  document.body.removeChild(textarea);
  if (!success) throw new Error('Copy was blocked by the browser.');
}

export default function Settings() {
  const { logout, updateUser } = useAuth();
  const profileFetch = useFetch(authService.me, []);
  const familiesFetch = useFetch(familyService.list, []);

  const [profile, setProfile] = useState({ full_name: '', email: '' });
  const [profileErrors, setProfileErrors] = useState({});
  const [profileError, setProfileError] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileSaved, setProfileSaved] = useState(false);

  const [newFamily, setNewFamily] = useState({ name: '', description: '' });
  const [newFamilyError, setNewFamilyError] = useState('');
  const [creatingFamily, setCreatingFamily] = useState(false);
  const [familySuccess, setFamilySuccess] = useState('');

  const [inviteCode, setInviteCode] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joining, setJoining] = useState(false);

  const [copiedKey, setCopiedKey] = useState('');
  const [copyError, setCopyError] = useState('');

  useEffect(() => {
    if (profileFetch.data) {
      setProfile({
        full_name: profileFetch.data.full_name || '',
        email: profileFetch.data.email || '',
      });
    }
  }, [profileFetch.data]);

  const copy = async (value, key) => {
    setCopyError('');
    try {
      await copyToClipboard(value);
      setCopiedKey(key);
      window.setTimeout(() => setCopiedKey((current) => (current === key ? '' : current)), 2000);
    } catch {
      setCopyError('Copying is not available in this browser. Select the text and copy it manually.');
    }
  };

  const copyInviteLink = async (family) => {
    setCopyError('');
    try {
      const data = await familyService.createInvite(family.id);
      if (!data?.invite_url) throw new Error('No invite link was returned.');
      await copyToClipboard(data.invite_url);
      setCopiedKey(`link-${family.id}`);
      window.setTimeout(() => setCopiedKey((current) => (current === `link-${family.id}` ? '' : current)), 2000);
    } catch (error) {
      setCopyError(getErrorMessage(error, 'Could not create an invite link.'));
    }
  };

  const saveProfile = async (event) => {
    event.preventDefault();
    const errors = {};
    if (!profile.full_name.trim()) errors.full_name = 'Enter your name.';
    if (!profile.email.trim()) errors.email = 'Enter your email address.';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profile.email.trim())) errors.email = 'Enter a valid email address.';
    setProfileErrors(errors);
    setProfileError('');
    setProfileSaved(false);
    if (Object.keys(errors).length) return;

    setSavingProfile(true);
    try {
      const updated = await authService.updateMe({
        full_name: profile.full_name.trim(),
        email: profile.email.trim(),
      });
      updateUser({ ...profileFetch.data, ...updated });
      setProfileSaved(true);
      profileFetch.reload();
    } catch (error) {
      setProfileError(getErrorMessage(error, 'Could not save your profile.'));
    } finally {
      setSavingProfile(false);
    }
  };

  const createFamily = async (event) => {
    event.preventDefault();
    if (!newFamily.name.trim()) {
      setNewFamilyError('Give your family a name.');
      return;
    }
    setCreatingFamily(true);
    setNewFamilyError('');
    setFamilySuccess('');
    try {
      const created = await familyService.create({
        name: newFamily.name.trim(),
        description: newFamily.description.trim(),
      });
      setNewFamily({ name: '', description: '' });
      setFamilySuccess(`“${created.name}” was created.`);
      familiesFetch.reload();
    } catch (error) {
      setNewFamilyError(getErrorMessage(error, 'Could not create the family.'));
    } finally {
      setCreatingFamily(false);
    }
  };

  const joinFamily = async (event) => {
    event.preventDefault();
    if (!inviteCode.trim()) {
      setJoinError('Enter the invite code you received.');
      return;
    }
    setJoining(true);
    setJoinError('');
    setFamilySuccess('');
    try {
      const joined = await familyService.join({ invite_code: inviteCode.trim() });
      setInviteCode('');
      setFamilySuccess(`You joined “${joined.name}”.`);
      familiesFetch.reload();
      profileFetch.reload();
    } catch (error) {
      setJoinError(getErrorMessage(error, 'That invite code did not work.'));
    } finally {
      setJoining(false);
    }
  };

  const families = Array.isArray(familiesFetch.data) ? familiesFetch.data : [];

  return (
    <>
      <PageHeader
        eyebrow="Settings"
        title="Your account and family"
        description="Keep your details up to date and manage the family groups you share checks with."
      />

      {copyError && (
        <div className="mb-5 flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-xs text-red-700" role="alert">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{copyError}</span>
        </div>
      )}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
        <div className="space-y-5">
          <section className="fs-card p-5 sm:p-6">
            <div className="mb-5 flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-navy-900/5 text-navy-700">
                <UserRound className="h-5 w-5" strokeWidth={1.8} />
              </span>
              <div>
                <h2 className="fs-section-title">Your profile</h2>
                <p className="mt-0.5 text-xs text-slate-400">Only you can change these details.</p>
              </div>
            </div>

            {profileFetch.loading ? (
              <LoadingState compact label="Loading profile…" />
            ) : profileFetch.error ? (
              <ErrorState error={profileFetch.error} onRetry={profileFetch.reload} title="Could not load your profile" />
            ) : (
              <>
                <div className="mb-5 flex items-center gap-3 rounded-xl border border-line bg-slate-50/60 p-3.5">
                  <span className="grid h-11 w-11 place-items-center rounded-full bg-navy-800 text-xs font-semibold text-white">
                    {initials(profile.full_name)}
                  </span>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-800">{profileFetch.data?.full_name}</p>
                    <p className="truncate text-xs text-slate-500">{profileFetch.data?.email}</p>
                  </div>
                </div>

                <form onSubmit={saveProfile} noValidate className="space-y-4">
                  {profileError && (
                    <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-xs text-red-700" role="alert">
                      <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      {profileError}
                    </div>
                  )}
                  {profileSaved && (
                    <div className="flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-xs text-emerald-700" role="status">
                      <Check className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      Your profile was updated.
                    </div>
                  )}
                  <div>
                    <label htmlFor="settings-name" className="fs-label">Full name</label>
                    <input
                      id="settings-name"
                      className={`fs-input ${profileErrors.full_name ? 'border-red-300' : ''}`}
                      value={profile.full_name}
                      onChange={(event) => {
                        setProfile((current) => ({ ...current, full_name: event.target.value }));
                        setProfileErrors((current) => ({ ...current, full_name: '' }));
                        setProfileSaved(false);
                      }}
                    />
                    {profileErrors.full_name && <p className="mt-1 text-xs text-red-600">{profileErrors.full_name}</p>}
                  </div>
                  <div>
                    <label htmlFor="settings-email" className="fs-label">Email address</label>
                    <input
                      id="settings-email"
                      type="email"
                      className={`fs-input ${profileErrors.email ? 'border-red-300' : ''}`}
                      value={profile.email}
                      onChange={(event) => {
                        setProfile((current) => ({ ...current, email: event.target.value }));
                        setProfileErrors((current) => ({ ...current, email: '' }));
                        setProfileSaved(false);
                      }}
                    />
                    {profileErrors.email && <p className="mt-1 text-xs text-red-600">{profileErrors.email}</p>}
                  </div>
                  <button type="submit" className="fs-btn-primary w-full" disabled={savingProfile}>
                    {savingProfile ? <Spinner className="h-4 w-4" /> : null}
                    {savingProfile ? 'Saving…' : 'Save changes'}
                  </button>
                </form>

                {Array.isArray(profileFetch.data?.families) && profileFetch.data.families.length > 0 && (
                  <div className="mt-5 border-t border-line pt-4">
                    <p className="fs-label">Your roles</p>
                    <div className="space-y-2">
                      {profileFetch.data.families.map((family) => (
                        <div key={family.id} className="flex items-center justify-between gap-3 text-xs">
                          <span className="truncate text-slate-600">{family.name}</span>
                          <RoleBadge role={family.role} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </section>

          <section className="fs-card p-5 sm:p-6">
            <h2 className="fs-section-title">Sign out</h2>
            <p className="mt-1.5 text-xs leading-relaxed text-slate-500">
              You will need to sign in again to view scans and family alerts.
            </p>
            <button type="button" onClick={logout} className="fs-btn-secondary mt-4 w-full text-red-600">
              <LogOut className="h-4 w-4" /> Log out
            </button>
          </section>
        </div>

        <div className="space-y-5">
          <section className="fs-card p-5 sm:p-6">
            <div className="mb-5 flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
                <UsersRound className="h-5 w-5" strokeWidth={1.8} />
              </span>
              <div>
                <h2 className="fs-section-title">Your families</h2>
                <p className="mt-0.5 text-xs text-slate-400">Invite codes let trusted relatives join privately.</p>
              </div>
            </div>

            {familySuccess && (
              <div className="mb-4 flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-xs text-emerald-700" role="status">
                <Check className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {familySuccess}
              </div>
            )}

            {familiesFetch.loading ? (
              <LoadingState compact label="Loading families…" />
            ) : familiesFetch.error ? (
              <ErrorState error={familiesFetch.error} onRetry={familiesFetch.reload} title="Could not load families" />
            ) : families.length === 0 ? (
              <EmptyState
                icon={UsersRound}
                title="No families yet"
                description="Create a family below, or join one using an invite code from a relative."
                compact
              />
            ) : (
              <div className="space-y-3">
                {families.map((family) => (
                  <div key={family.id} className="rounded-xl border border-line bg-slate-50/50 p-4">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{family.name}</p>
                        {family.description && <p className="mt-0.5 text-xs text-slate-500">{family.description}</p>}
                      </div>
                      <RoleBadge role={family.my_role} />
                    </div>
                    <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-400">
                      {Array.isArray(family.members) && <span>{family.members.length} {family.members.length === 1 ? 'member' : 'members'}</span>}
                      {family.created_at && <span>Created {formatDate(family.created_at)}</span>}
                    </div>
                    {family.invite_code && (
                      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-line pt-3">
                        <div className="min-w-0">
                          <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-400">Invite code</p>
                          <p className="font-mono text-[13px] font-semibold tracking-wide text-slate-700">{family.invite_code}</p>
                        </div>
                        <div className="ml-auto flex gap-2">
                          <button type="button" className="fs-btn-secondary px-3 py-1.5 text-xs" onClick={() => copy(family.invite_code, `code-${family.id}`)}>
                            {copiedKey === `code-${family.id}` ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                            {copiedKey === `code-${family.id}` ? 'Copied' : 'Copy code'}
                          </button>
                          <button type="button" className="fs-btn-secondary px-3 py-1.5 text-xs" onClick={() => copyInviteLink(family)}>
                            {copiedKey === `link-${family.id}` ? <Check className="h-3.5 w-3.5" /> : <Link2 className="h-3.5 w-3.5" />}
                            {copiedKey === `link-${family.id}` ? 'Copied' : 'Invite link'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          <div className="grid gap-5 md:grid-cols-2">
            <section className="fs-card p-5">
              <h3 className="text-sm font-semibold text-slate-900">Create a family</h3>
              <p className="mt-1 text-xs text-slate-500">You will be the administrator.</p>
              <form onSubmit={createFamily} noValidate className="mt-4 space-y-3">
                {newFamilyError && <p className="text-xs font-medium text-red-600">{newFamilyError}</p>}
                <div>
                  <label htmlFor="new-family-name" className="fs-label">Family name</label>
                  <input
                    id="new-family-name"
                    className="fs-input"
                    value={newFamily.name}
                    onChange={(event) => {
                      setNewFamily((current) => ({ ...current, name: event.target.value }));
                      setNewFamilyError('');
                    }}
                    placeholder="e.g. Kumar Family"
                  />
                </div>
                <div>
                  <label htmlFor="new-family-description" className="fs-label">Description (optional)</label>
                  <input
                    id="new-family-description"
                    className="fs-input"
                    value={newFamily.description}
                    onChange={(event) => setNewFamily((current) => ({ ...current, description: event.target.value }))}
                    placeholder="A short note about this group"
                  />
                </div>
                <button type="submit" className="fs-btn-primary w-full" disabled={creatingFamily}>
                  {creatingFamily ? <Spinner className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                  {creatingFamily ? 'Creating…' : 'Create family'}
                </button>
              </form>
            </section>

            <section className="fs-card p-5">
              <h3 className="text-sm font-semibold text-slate-900">Join a family</h3>
              <p className="mt-1 text-xs text-slate-500">Use a code shared by a family administrator.</p>
              <form onSubmit={joinFamily} noValidate className="mt-4 space-y-3">
                {joinError && <p className="text-xs font-medium text-red-600">{joinError}</p>}
                <div>
                  <label htmlFor="join-code" className="fs-label">Invite code</label>
                  <input
                    id="join-code"
                    className="fs-input font-mono uppercase tracking-wide"
                    value={inviteCode}
                    onChange={(event) => {
                      setInviteCode(event.target.value);
                      setJoinError('');
                    }}
                    placeholder="FS-ABCD12EF"
                  />
                </div>
                <button type="submit" className="fs-btn-secondary w-full" disabled={joining}>
                  {joining ? <Spinner className="h-4 w-4" /> : <UsersRound className="h-4 w-4" />}
                  {joining ? 'Joining…' : 'Join family'}
                </button>
              </form>
            </section>
          </div>
        </div>
      </div>

      <AdvisoryNote className="mt-6" />
    </>
  );
}
