/**
 * Swizzled Component: DocItem/Layout (WRAP mode)
 * Purpose: Inject ContentButtons above doc content (FR-019, FR-020)
 * Original: @docusaurus/theme-classic/src/theme/DocItem/Layout
 * Swizzled: 2025-12-16
 * Feature: 002-fix-ui-theme
 */
import React, {type ReactNode} from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import ContentButtons from '@site/src/components/ContentButtons';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): ReactNode {
  return (
    <>
      <ContentButtons />
      <Layout {...props} />
    </>
  );
}
