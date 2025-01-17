import { FormPageI } from '~/interfaces/form/form-page-i'

const createStep = (
  label: string,
  icon: string,
  alt: string,
  title: string,
  subtitle: string,
  formTitle: string,
  complete: boolean = false,
  isValid: boolean = false,
  sections: any[] = []
): FormPageI => ({
  step: {
    label: `createAccount.stepTitle.${label}`,
    inactiveIconPath: `/icons/create-account/${icon}.svg`,
    activeIconPath: `/icons/create-account/${icon}_active.svg`,
    complete,
    isValid,
    alt
  },
  title: title ? `createAccount.${title}.title` : '',
  subtitle: subtitle ? `createAccount.${subtitle}.subtitle` : '',
  formTitle: formTitle ? `createAccount.${formTitle}.primary` : '',
  sections
})

const steps: FormPageI[] = [
  createStep(
    'propertyManager',
    'add_property_manager',
    'Add property managers',
    'propertyManager',
    'propertyManager',
    'propertyManager'
  ),
  createStep('contact', 'account_multiple_plus', 'Add contacts', 'contact', 'contact', 'contact'),
  createStep('property', 'add_location', 'Add properties', 'details', 'details', 'details'),
  createStep('eligibility', 'home_owner', 'Upload documents', 'eligibility', '', 'eligibility'),
  createStep('review', 'text_box_check', 'Check and verify', 'confirm', '', 'confirm')
]

export default steps
