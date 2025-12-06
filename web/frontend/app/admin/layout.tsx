/**
 * Admin Panel Layout with Sidebar Navigation
 */
'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useStore } from '@/lib/store';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import {
  LayoutDashboard,
  Users,
  Settings,
  Shield,
  Activity,
  ChevronLeft,
  Menu,
  X
} from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Check if user is admin
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    // TODO: Check if user has admin role
    // For now, allow all authenticated users (temporary)
    // if (!user.is_admin) {
    //   router.push('/');
    // }
  }, [user, router]);

  const navItems = [
    {
      href: '/admin',
      label: 'Dashboard',
      icon: LayoutDashboard,
      description: 'System overview & health'
    },
    {
      href: '/admin/users',
      label: 'Users',
      icon: Users,
      description: 'User management'
    },
    {
      href: '/admin/settings',
      label: 'Settings',
      icon: Settings,
      description: 'Feature toggles & config'
    },
    {
      href: '/admin/audit-logs',
      label: 'Audit Logs',
      icon: Activity,
      description: 'Security events'
    },
  ];

  const isActive = (href: string) => {
    if (href === '/admin') {
      return pathname === href;
    }
    return pathname?.startsWith(href);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-800 border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-6 w-6 text-primary" />
          <span className="font-bold text-lg">Admin Panel</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      <div className="flex lg:pt-0 pt-16">
        {/* Sidebar */}
        <aside
          className={`
            fixed lg:sticky top-16 lg:top-0 left-0 h-[calc(100vh-4rem)] lg:h-screen
            w-72 bg-white dark:bg-gray-800 border-r
            transition-transform duration-300 ease-in-out z-40
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          `}
        >
          <div className="p-6 hidden lg:flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-primary" />
              <div>
                <h2 className="font-bold text-lg">Admin Panel</h2>
                <p className="text-xs text-muted-foreground">System Management</p>
              </div>
            </div>
            <ThemeToggle />
          </div>

          <Separator className="hidden lg:block" />

          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                >
                  <div
                    className={`
                      flex items-start gap-3 p-3 rounded-lg transition-colors
                      ${active
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium">{item.label}</div>
                      <div className={`text-xs ${active ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
                        {item.description}
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </nav>

          <Separator />

          <div className="p-4">
            <div className="bg-muted/50 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Logged in as</span>
                <Badge variant="secondary" className="text-xs">Admin</Badge>
              </div>
              <p className="text-sm text-muted-foreground truncate">
                {user?.username || 'Unknown'}
              </p>
              <Separator className="my-3" />
              <Link href="/">
                <Button variant="outline" size="sm" className="w-full">
                  <ChevronLeft className="h-4 w-4 mr-2" />
                  Back to Chat
                </Button>
              </Link>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-h-screen lg:min-h-0">
          <div className="max-w-7xl mx-auto p-6">
            {children}
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
