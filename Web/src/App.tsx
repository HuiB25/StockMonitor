import React, { useEffect, useState } from 'react';
import { Layout, Typography, Card, Form, Input, InputNumber, Switch, Button, Table, Space, message } from 'antd';
import { PlusOutlined, DeleteOutlined, ReloadOutlined, SaveOutlined } from '@ant-design/icons';
import { getConfig, getStatus, updateConfig } from './api';
import { Config } from './types';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const App: React.FC = () => {
  const [config, setConfig] = useState<Config | null>(null);
  const [status, setStatus] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  const fetchData = async () => {
    setLoading(true);
    try {
      const [configData, statusData] = await Promise.all([getConfig(), getStatus()]);
      setConfig(configData);
      setStatus(statusData.message);
      form.setFieldsValue(configData);
    } catch (error) {
      console.error(error);
      message.error('Failed to load data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh status every 5 seconds
    const interval = setInterval(() => {
        getStatus().then(res => setStatus(res.message)).catch(() => {});
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const onFinish = async (values: Config) => {
    try {
      await updateConfig(values);
      message.success('Configuration saved successfully');
      setConfig(values);
    } catch (error) {
      message.error('Failed to save configuration');
    }
  };

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>Stock Monitor</Title>
      </Header>
      <Content style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            
          {/* Status Dashboard */}
          <Card title="System Status" extra={<Button icon={<ReloadOutlined />} onClick={fetchData}>Refresh</Button>}>
            <Text style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>{status || 'Loading...'}</Text>
          </Card>

          {/* Configuration Form */}
          <Card title="Configuration">
            {config ? (
              <Form form={form} layout="vertical" onFinish={onFinish} initialValues={config}>
                
                <Title level={5}>Settings</Title>
                <Space wrap size="large" style={{ marginBottom: 20 }}>
                    <Form.Item name={['settings', 'refresh_interval_seconds']} label="刷新间隔 (s)" rules={[{ required: true }]}>
                        <InputNumber min={1} />
                    </Form.Item>
                    <Form.Item name={['settings', 'alert_interval_seconds']} label="通知间隔 (s)" rules={[{ required: true }]}>
                        <InputNumber min={1} />
                    </Form.Item>
                    <Form.Item name={['settings', 'notification_enabled']} label="是否通知" valuePropName="checked">
                        <Switch />
                    </Form.Item>
                    {/* <Form.Item name={['settings', 'send_key']} label="通知密钥" style={{ minWidth: 300 }}>
                        <Input.Password />
                    </Form.Item> */}
                </Space>

                <Title level={5}>Portfolio</Title>
                <Form.List name="portfolio">
                  {(fields, { add, remove }) => (
                    <>
                      <Table
                        dataSource={fields}
                        pagination={false}
                        rowKey="key"
                        size="small"
                        columns={[
                            {
                                title: '代码',
                                dataIndex: 'code',
                                render: (_, field) => (
                                    <Form.Item {...field} name={[field.name, 'code']} noStyle rules={[{ required: true }]}>
                                        <Input placeholder="sh000001" />
                                    </Form.Item>
                                )
                            },
                            {
                                title: '名称',
                                dataIndex: 'name',
                                render: (_, field) => (
                                    <Form.Item {...field} name={[field.name, 'name']} noStyle rules={[{ required: true }]}>
                                        <Input placeholder="Name" />
                                    </Form.Item>
                                )
                            },
                            {
                                title: '持有股数',
                                dataIndex: 'held_shares',
                                render: (_, field) => (
                                    <Form.Item {...field} name={[field.name, 'held_shares']} noStyle rules={[{ required: true }]}>
                                        <InputNumber min={0} style={{ width: '100%' }} />
                                    </Form.Item>
                                )
                            },
                            {
                                title: 'Min %',
                                dataIndex: 'min_percentage',
                                render: (_, field) => (
                                    <Form.Item {...field} name={[field.name, 'min_percentage']} noStyle rules={[{ required: true }]}>
                                        <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} />
                                    </Form.Item>
                                )
                            },
                            {
                                title: 'Max %',
                                dataIndex: 'max_percentage',
                                render: (_, field) => (
                                    <Form.Item {...field} name={[field.name, 'max_percentage']} noStyle rules={[{ required: true }]}>
                                        <InputNumber min={0} max={100} step={0.1} style={{ width: '100%' }} />
                                    </Form.Item>
                                )
                            },
                            {
                                title: '删除',
                                width: 60,
                                render: (_, field) => (
                                    <Button type="text" danger icon={<DeleteOutlined />} onClick={() => remove(field.name)} />
                                )
                            }
                        ]}
                      />
                      <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />} style={{ marginTop: 10 }}>
                        新增
                      </Button>
                    </>
                  )}
                </Form.List>

                <Form.Item style={{ marginTop: 20 }}>
                  <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
                    保存配置
                  </Button>
                </Form.Item>
              </Form>
            ) : (
                <Text>Loading config...</Text>
            )}
          </Card>
        </Space>
      </Content>
    </Layout>
  );
};

export default App;