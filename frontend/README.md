# MFG���� ���Ȩ�ɷ���

MFG���������q����n���Ȩ�ɡ;bgY

## �S��ï

- **React 18** + **TypeScript**
- **Vite** (������)
- **Material-UI (MUI)** (UI�������)
- **Redux Toolkit** + **RTK Query** (�K�)
- **React Router** (��ƣ�)
- **Vitest** + **React Testing Library** (ƹ�)

## �z����

### M�a�

- Node.js 18.x �

- npm ~_o yarn

### �����

```bash
# �X��n�����
npm install

# �z����w�
npm run dev
```

�z����o http://localhost:3000 gw�W~Y

### )(��j�����

```bash
# �z����w�
npm run dev

# ����������
npm run build

# ���n�����
npm run preview

# ƹȟL
npm run test

# ƹ�UI���	
npm run test:ui

# ���ø�Mƹ�
npm run test:coverage

# ���ï
npm run type-check

# Lint�L
npm run lint

# Lint�c
npm run lint:fix
```

## ������� 

```
src/
   components/          # �)(��jUI�������
      common/         # q�������
      drone/          # ����#�������
      vision/         # Ӹ��#�������
      dashboard/      # �÷���ɢ#
   pages/              # ����������
   hooks/              # ����React�ï
   services/           # Ӹ͹��ï�API
   store/              # Redux�K�
   types/              # TypeScript���
   utils/              # ��ƣ�ƣ�p
   styles/             # ���뚩
   test/               # ƹ�-�
```

## �z�����

### ��ɹ���

- ESLint + Prettier �(
- TypeScript n�<��ɒ	�
- �������o�p�������g\
- Material-UI n��޷����;(

### �K�

- �����K: Redux Toolkit
- �����K: RTK Query
- թ��K: React Hook Form
- ����K: useState/useReducer

### ƹ�

- XSƹ�: Vitest + React Testing Library
- ���ø�: 90%�

- E2Eƹ�: Playwright (e��)

## Docker gn�L

### �z��

```bash
docker build --target development -t mfg-drone-frontend:dev .
docker run -p 3000:3000 -v $(pwd):/app mfg-drone-frontend:dev
```

### �������

```bash
docker build --target production -t mfg-drone-frontend:prod .
docker run -p 80:80 mfg-drone-frontend:prod
```

## API #:

�ï���APIhn#:o�n-�gLD~Y

- �z��: `http://localhost:8000`
- WebSocket: `ws://localhost:8000`
- ����-�: `vite.config.ts` g-�

## �������

### ��	p

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL  
VITE_WS_URL=ws://localhost:8000

# Environment
VITE_NODE_ENV=production
```

### ���

```bash
npm run build
```

����io `dist/` ǣ���k��U�~Y

## 餻�

Sn������o MIT 餻�gY

## \

- Claude Code
- \�: 2025-07-03